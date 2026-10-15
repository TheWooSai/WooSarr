"""Test database migrations."""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import sqlite3
import tempfile
from pathlib import Path

from alembic.config import Config
from alembic import command


@pytest.fixture
def alembic_config(tmp_path):
    """Create a temporary alembic config for testing."""
    # Create a temporary database
    db_path = tmp_path / "test.db"

    # Use the actual alembic.ini but override the database URL
    config = Config(str(Path(__file__).parent.parent / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    return config, db_path


def test_migrations_run_cleanly(alembic_config):
    """Test that migrations run without errors."""
    config, db_path = alembic_config

    # Run upgrade
    command.upgrade(config, "head")

    # Verify tables were created
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Check expected tables exist
    expected_tables = [
        "alembic_version",
        "discord_users",
        "libraries",
        "library_roles",
        "logs",
        "plex_users",
        "roles",
        "settings",
        "users",
    ]
    for table in expected_tables:
        assert table in tables, f"Table {table} not found in database"


def test_downgrade_works(alembic_config):
    """Test that downgrade works."""
    config, db_path = alembic_config

    # Run upgrade
    command.upgrade(config, "head")

    # Run downgrade
    command.downgrade(config, "base")

    # Verify tables were dropped
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Only alembic_version should remain
    assert tables == ["alembic_version"]