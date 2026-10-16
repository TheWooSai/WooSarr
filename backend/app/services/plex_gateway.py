"""Plex Gateway interface and implementations.

This module defines the PlexGateway interface that abstracts all Plex API interactions.
Two implementations are provided:
1. PlexApiGateway - real implementation using python-plexapi
2. FakePlexGateway - in-memory implementation for testing
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Set


@dataclass
class PlexUser:
    """Represents a Plex user."""
    id: str
    username: str
    email: Optional[str] = None
    thumb: Optional[str] = None
    is_home_user: bool = False
    is_restricted: bool = False


@dataclass
class PlexLibrary:
    """Represents a Plex library."""
    key: int
    title: str
    type: str  # 'movies', 'shows', 'music', etc.
    agent: str


@dataclass
class PlexServerInfo:
    """Represents Plex server information."""
    machine_identifier: str
    friendly_name: str
    version: Optional[str] = None


class PlexGateway(ABC):
    """Abstract interface for Plex API interactions."""

    @abstractmethod
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with Plex using username and password."""
        pass

    @abstractmethod
    def authenticate_with_token(self, token: str) -> bool:
        """Authenticate with Plex using an auth token."""
        pass

    @abstractmethod
    def list_users(self) -> List[PlexUser]:
        """List all users (friends) of the Plex account."""
        pass

    @abstractmethod
    def list_libraries(self) -> List[PlexLibrary]:
        """List all libraries on the server."""
        pass

    @abstractmethod
    def get_server_info(self) -> PlexServerInfo:
        """Get information about the Plex server."""
        pass

    @abstractmethod
    def get_user_shared_library_keys(self, user: PlexUser) -> Set[int]:
        """Get the set of library keys shared with a user."""
        pass

    @abstractmethod
    def set_user_libraries(self, user: PlexUser, library_keys: Set[int]) -> bool:
        """Set the libraries shared with a user (replaces existing)."""
        pass

    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        pass

    @abstractmethod
    def get_auth_token(self) -> Optional[str]:
        """Get the current auth token."""
        pass