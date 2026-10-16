"""Tests for Plex Gateway interface and implementations."""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from app.services.fake_plex_gateway import FakePlexGateway
from app.services.plex_gateway import PlexLibrary, PlexUser


def test_fake_plex_gateway_authentication():
    """Test fake gateway authentication."""
    gateway = FakePlexGateway()

    # Not authenticated initially
    assert not gateway.is_authenticated()
    assert gateway.get_auth_token() is None

    # Authenticate with correct credentials
    assert gateway.authenticate("test", "test") is True
    assert gateway.is_authenticated() is True
    assert gateway.get_auth_token() == "fake-token"

    # Authenticate with wrong credentials
    gateway2 = FakePlexGateway()
    assert gateway2.authenticate("wrong", "wrong") is False


def test_fake_plex_gateway_token_authentication():
    """Test fake gateway token authentication."""
    gateway = FakePlexGateway()

    # Authenticate with correct token
    assert gateway.authenticate_with_token("fake-token") is True
    assert gateway.is_authenticated() is True

    # Authenticate with wrong token
    gateway2 = FakePlexGateway()
    assert gateway2.authenticate_with_token("wrong-token") is False


def test_fake_plex_gateway_users():
    """Test fake gateway user management."""
    gateway = FakePlexGateway()

    # Add users
    user1 = PlexUser(id="1", username="user1")
    user2 = PlexUser(id="2", username="user2")
    gateway.add_user(user1)
    gateway.add_user(user2)

    # List users
    users = gateway.list_users()
    assert len(users) == 2
    assert users[0].username == "user1"
    assert users[1].username == "user2"


def test_fake_plex_gateway_libraries():
    """Test fake gateway library management."""
    gateway = FakePlexGateway()

    # Add libraries
    lib1 = PlexLibrary(key=1, title="Movies", type="movies", agent="movie.agents.themoviedb")
    lib2 = PlexLibrary(key=2, title="TV Shows", type="shows", agent="tv.agents.thetvdb")
    gateway.add_library(lib1)
    gateway.add_library(lib2)

    # List libraries
    libraries = gateway.list_libraries()
    assert len(libraries) == 2
    assert libraries[0].title == "Movies"
    assert libraries[1].title == "TV Shows"


def test_fake_plex_gateway_user_libraries():
    """Test fake gateway user library sharing."""
    gateway = FakePlexGateway()

    # Add user and libraries
    user = PlexUser(id="1", username="user1")
    lib1 = PlexLibrary(key=1, title="Movies", type="movies", agent="movie.agents.themoviedb")
    lib2 = PlexLibrary(key=2, title="TV Shows", type="shows", agent="tv.agents.thetvdb")
    gateway.add_user(user)
    gateway.add_library(lib1)
    gateway.add_library(lib2)

    # Initially no shared libraries
    assert gateway.get_user_shared_library_keys(user) == set()

    # Share libraries with user
    assert gateway.set_user_libraries(user, {1, 2}) is True
    assert gateway.get_user_shared_library_keys(user) == {1, 2}

    # Update shared libraries
    assert gateway.set_user_libraries(user, {1}) is True
    assert gateway.get_user_shared_library_keys(user) == {1}


def test_fake_plex_gateway_server_info():
    """Test fake gateway server info."""
    gateway = FakePlexGateway()

    info = gateway.get_server_info()
    assert info.machine_identifier == "fake-machine-id"
    assert info.friendly_name == "Fake Plex Server"
    assert info.version == "1.0.0"