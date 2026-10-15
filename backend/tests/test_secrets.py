"""Test secrets manager."""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import tempfile
from pathlib import Path

from app.core.secrets import SecretsManager
from app.core import config


@pytest.fixture
def secrets_manager():
    """Create a secrets manager with a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Set up temporary paths
        original_config_dir = config.settings.CONFIG_DIR
        original_secrets_dir = config.settings.SECRETS_DIR
        original_master_key = config.settings.MASTER_KEY_PATH

        config.settings.CONFIG_DIR = Path(tmpdir)
        config.settings.SECRETS_DIR = Path(tmpdir) / "secrets"
        config.settings.MASTER_KEY_PATH = Path(tmpdir) / "secrets" / "master.key"

        manager = SecretsManager()

        yield manager

        # Restore original paths
        config.settings.CONFIG_DIR = original_config_dir
        config.settings.SECRETS_DIR = original_secrets_dir
        config.settings.MASTER_KEY_PATH = original_master_key


def test_key_generation(secrets_manager):
    """Test that key generation produces 32-byte keys."""
    key = secrets_manager.generate_key()
    assert len(key) == 32


def test_encrypt_decrypt(secrets_manager):
    """Test that encryption and decryption work correctly."""
    plaintext = "my-secret-token"
    encrypted = secrets_manager.encrypt(plaintext)

    # Verify encryption produces different output each time (due to nonce)
    encrypted2 = secrets_manager.encrypt(plaintext)
    assert encrypted != encrypted2

    # Verify decryption returns original
    decrypted = secrets_manager.decrypt(encrypted)
    assert decrypted == plaintext

    decrypted2 = secrets_manager.decrypt(encrypted2)
    assert decrypted2 == plaintext


def test_key_file_permissions(secrets_manager):
    """Test that master key file has 0600 permissions."""
    secrets_manager.rotate_key()

    key_path = config.settings.MASTER_KEY_PATH
    mode = os.stat(key_path).st_mode
    # Check owner read/write only (0600)
    assert mode & 0o777 == 0o600


def test_secrets_dir_permissions(secrets_manager):
    """Test that secrets directory has 0700 permissions."""
    secrets_manager.rotate_key()  # This creates the directory

    secrets_dir = config.settings.SECRETS_DIR
    mode = os.stat(secrets_dir).st_mode
    # Check owner rwx only (0700)
    assert mode & 0o777 == 0o700


def test_mask(secrets_manager):
    """Test secret masking."""
    # Short string (5 chars) with 4 visible -> 1 star + 4 chars
    assert secrets_manager.mask("short") == "*hort"
    # Long string
    assert secrets_manager.mask("my-secret-token") == "***********oken"
    # Custom visible chars
    assert secrets_manager.mask("abcdef", 2) == "****ef"
    # String shorter than visible chars
    assert secrets_manager.mask("ab", 4) == "**"


def test_rotate_key(secrets_manager):
    """Test key rotation."""
    # Encrypt with original key
    plaintext = "test-value"
    encrypted = secrets_manager.encrypt(plaintext)

    # Rotate key
    secrets_manager.rotate_key()

    # Old encrypted value should fail to decrypt
    with pytest.raises(Exception):
        secrets_manager.decrypt(encrypted)

    # New encryption should work
    new_encrypted = secrets_manager.encrypt(plaintext)
    assert secrets_manager.decrypt(new_encrypted) == plaintext