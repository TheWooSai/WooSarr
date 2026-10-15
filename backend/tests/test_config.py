"""Test configuration loader."""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from pathlib import Path

from app.core.config import Settings


def test_default_settings():
    """Test that default settings are loaded correctly."""
    settings = Settings()
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 2000
    assert settings.CONFIG_DIR == Path("/config")
    assert settings.DB_PATH == Path("/config/woosarr.db")


def test_env_var_override():
    """Test that environment variables override defaults."""
    os.environ["WOOSARR_PORT"] = "3000"
    os.environ["WOOSARR_HOST"] = "127.0.0.1"
    try:
        settings = Settings()
        assert settings.PORT == 3000
        assert settings.HOST == "127.0.0.1"
    finally:
        del os.environ["WOOSARR_PORT"]
        del os.environ["WOOSARR_HOST"]


def test_no_secrets_in_defaults():
    """Test that no secrets are in default values."""
    settings = Settings()
    assert settings.DISCORD_BOT_TOKEN == ""
    assert settings.PLEX_TOKEN == ""