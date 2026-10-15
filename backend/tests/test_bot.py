"""Test Discord bot skeleton."""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, MagicMock

from app.bot import create_bot, WooSarrBot


def test_bot_creation():
    """Test that bot can be created."""
    bot = create_bot()
    assert isinstance(bot, WooSarrBot)
    assert bot.command_prefix == "!"


def test_bot_has_intents():
    """Test that bot has proper intents configured."""
    bot = create_bot()
    assert bot.intents.message_content
    assert bot.intents.members


def test_bot_run_with_mock():
    """Test that run_bot calls bot.run with the configured token."""
    from app.bot import run_bot
    from app.core import config

    with patch("app.bot.create_bot") as mock_create, patch.object(
        config.settings, "DISCORD_BOT_TOKEN", "test-token"
    ):
        mock_bot = MagicMock()
        mock_create.return_value = mock_bot

        run_bot()

        mock_create.assert_called_once()
        mock_bot.run.assert_called_once_with("test-token")


def test_ping_command_registered():
    """Test that ping command is registered."""
    from app.bot import run_bot
    from app.core import config

    with patch("app.bot.create_bot") as mock_create, patch.object(
        config.settings, "DISCORD_BOT_TOKEN", "test-token"
    ):
        mock_bot = MagicMock()
        mock_create.return_value = mock_bot

        run_bot()

        # Check that tree.command was called for ping
        assert any(
            call.kwargs.get("name") == "ping"
            for call in mock_bot.tree.command.call_args_list
        )