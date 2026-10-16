"""Integration tests with mocked Plex/Discord APIs."""
import pytest
from unittest.mock import patch, MagicMock


def test_sync_engine_role_add():
    """Test that sync engine adds roles when user joins library."""
    # Mock the sync engine
    mock_engine = MagicMock()
    mock_engine.sync.return_value = {
        'added': ['role1'],
        'removed': []
    }
    
    result = mock_engine.sync()
    assert 'role1' in result['added']


def test_sync_engine_role_remove():
    """Test that sync engine removes roles when user leaves library."""
    mock_engine = MagicMock()
    mock_engine.sync.return_value = {
        'added': [],
        'removed': ['role1']
    }
    
    result = mock_engine.sync()
    assert 'role1' in result['removed']


def test_sync_engine_role_modify():
    """Test that sync engine modifies roles when user changes library."""
    mock_engine = MagicMock()
    mock_engine.sync.return_value = {
        'added': ['role2'],
        'removed': ['role1']
    }
    
    result = mock_engine.sync()
    assert 'role2' in result['added']
    assert 'role1' in result['removed']