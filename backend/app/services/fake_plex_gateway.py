"""Fake in-memory Plex Gateway for testing."""

from typing import Dict, List, Optional, Set

from app.services.plex_gateway import (
    PlexGateway,
    PlexLibrary,
    PlexServerInfo,
    PlexUser,
)


class FakePlexGateway(PlexGateway):
    """In-memory Plex Gateway for testing."""

    def __init__(self):
        self._authenticated = False
        self._auth_token: Optional[str] = None
        self._users: List[PlexUser] = []
        self._libraries: List[PlexLibrary] = []
        self._user_libraries: Dict[str, Set[int]] = {}
        self._server_info = PlexServerInfo(
            machine_identifier="fake-machine-id",
            friendly_name="Fake Plex Server",
            version="1.0.0",
        )

    def add_user(self, user: PlexUser):
        """Add a user to the fake gateway."""
        self._users.append(user)
        if user.id not in self._user_libraries:
            self._user_libraries[user.id] = set()

    def add_library(self, library: PlexLibrary):
        """Add a library to the fake gateway."""
        self._libraries.append(library)

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with fake credentials."""
        if username == "test" and password == "test":
            self._authenticated = True
            self._auth_token = "fake-token"
            return True
        return False

    def authenticate_with_token(self, token: str) -> bool:
        """Authenticate with a fake token."""
        if token == "fake-token":
            self._authenticated = True
            self._auth_token = token
            return True
        return False

    def list_users(self) -> List[PlexUser]:
        """List all fake users."""
        return self._users.copy()

    def list_libraries(self) -> List[PlexLibrary]:
        """List all fake libraries."""
        return self._libraries.copy()

    def get_server_info(self) -> PlexServerInfo:
        """Get fake server info."""
        return self._server_info

    def get_user_shared_library_keys(self, user: PlexUser) -> Set[int]:
        """Get the set of library keys shared with a user."""
        return self._user_libraries.get(user.id, set()).copy()

    def set_user_libraries(self, user: PlexUser, library_keys: Set[int]) -> bool:
        """Set the libraries shared with a user."""
        self._user_libraries[user.id] = library_keys.copy()
        return True

    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        return self._authenticated

    def get_auth_token(self) -> Optional[str]:
        """Get the current auth token."""
        return self._auth_token