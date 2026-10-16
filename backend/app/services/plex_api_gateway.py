"""Real Plex Gateway implementation using python-plexapi."""

from typing import List, Optional, Set

from plexapi.server import PlexServer

from app.services.plex_gateway import (
    PlexGateway,
    PlexLibrary,
    PlexServerInfo,
    PlexUser,
)


class PlexApiGateway(PlexGateway):
    """Real Plex Gateway implementation using python-plexapi."""

    def __init__(self, server_url: str, token: Optional[str] = None):
        self._server_url = server_url
        self._token = token
        self._server: Optional[PlexServer] = None

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with Plex using username and password."""
        try:
            from plexapi.myplex import MyPlexAccount

            account = MyPlexAccount(username, password)
            self._token = account.auth_token
            return True
        except Exception:
            return False

    def authenticate_with_token(self, token: str) -> bool:
        """Authenticate with Plex using an auth token."""
        self._token = token
        try:
            self._server = PlexServer(self._server_url, token)
            return True
        except Exception:
            return False

    def list_users(self) -> List[PlexUser]:
        """List all users (friends) of the Plex account."""
        if not self._token:
            return []

        try:
            from plexapi.myplex import MyPlexAccount

            account = MyPlexAccount(token=self._token)
            users = []
            for friend in account.friends():
                users.append(PlexUser(
                    id=str(friend.id),
                    username=friend.username,
                    email=friend.email,
                    thumb=friend.thumb,
                ))
            return users
        except Exception:
            return []

    def list_libraries(self) -> List[PlexLibrary]:
        """List all libraries on the server."""
        if not self._server:
            return []

        try:
            libraries = []
            for section in self._server.library.sections():
                libraries.append(PlexLibrary(
                    key=section.key,
                    title=section.title,
                    type=section.type,
                    agent=section.agent,
                ))
            return libraries
        except Exception:
            return []

    def get_server_info(self) -> PlexServerInfo:
        """Get information about the Plex server."""
        if not self._server:
            return PlexServerInfo(
                machine_identifier="",
                friendly_name="",
            )

        try:
            return PlexServerInfo(
                machine_identifier=self._server.machineIdentifier,
                friendly_name=self._server.friendlyName,
                version=self._server.version,
            )
        except Exception:
            return PlexServerInfo(
                machine_identifier="",
                friendly_name="",
            )

    def get_user_shared_library_keys(self, user: PlexUser) -> Set[int]:
        """Get the set of library keys shared with a user."""
        if not self._token:
            return set()

        try:
            from plexapi.myplex import MyPlexAccount

            account = MyPlexAccount(token=self._token)
            library_keys = set()

            for share in account.sharedLibraries():
                if share.ownerID == user.id:
                    library_keys.add(share.key)

            return library_keys
        except Exception:
            return set()

    def set_user_libraries(self, user: PlexUser, library_keys: Set[int]) -> bool:
        """Set the libraries shared with a user (replaces existing)."""
        if not self._token:
            return False

        try:
            from plexapi.myplex import MyPlexAccount

            account = MyPlexAccount(token=self._token)

            # Get current shares for this user
            current_shares = [
                share for share in account.sharedLibraries()
                if share.ownerID == user.id
            ]

            # Remove shares not in the new set
            for share in current_shares:
                if share.key not in library_keys:
                    share.delete()

            # Add shares not already shared
            for key in library_keys:
                already_shared = any(share.key == key for share in current_shares)
                if not already_shared:
                    # Find the library section
                    for section in self._server.library.sections():
                        if section.key == key:
                            account.shareSection(section, user.username)
                            break

            return True
        except Exception:
            return False

    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        return self._token is not None and self._server is not None

    def get_auth_token(self) -> Optional[str]:
        """Get the current auth token."""
        return self._token

    def list_servers(self) -> List[PlexServerInfo]:
        """List all servers owned by the authenticated account."""
        if not self._token:
            return []

        try:
            from plexapi.myplex import MyPlexAccount

            account = MyPlexAccount(token=self._token)
            servers = []
            for resource in account.resources():
                if resource.product == "Plex Media Server":
                    servers.append(PlexServerInfo(
                        machine_identifier=resource.machineIdentifier,
                        friendly_name=resource.name,
                    ))
            return servers
        except Exception:
            return []