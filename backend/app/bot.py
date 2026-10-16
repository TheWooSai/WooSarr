"""Discord bot lifecycle manager."""

import asyncio
from typing import Optional

import discord
from discord.ext import commands

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.secrets import SecretsManager

logger = setup_logging()


class WooSarrBot(commands.Bot):
    """WooSarr Discord bot."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Bot is ready. Logged in as {self.user}")

    async def on_member_update(self, before, after):
        """Called when a member's roles change."""
        if before.roles != after.roles:
            logger.info(f"Member {after.display_name} roles changed")
            # Emit event to sync engine
            # TODO: Implement event queue

    async def on_role_update(self, role):
        """Called when a role is updated."""
        logger.info(f"Role {role.name} updated")
        # Emit event to sync engine
        # TODO: Implement event queue

    async def on_role_delete(self, role):
        """Called when a role is deleted."""
        logger.info(f"Role {role.name} deleted")
        # Emit event to sync engine
        # TODO: Implement event queue

    async def on_member_join(self, member):
        """Called when a member joins."""
        logger.info(f"Member {member.display_name} joined")
        # Emit event to sync engine
        # TODO: Implement event queue

    async def on_member_remove(self, member):
        """Called when a member leaves."""
        logger.info(f"Member {member.display_name} left")
        # Emit event to sync engine
        # TODO: Implement event queue


class BotManager:
    """Manages the Discord bot lifecycle."""

    def __init__(self):
        self._bot: Optional[WooSarrBot] = None
        self._running = False

    def is_running(self) -> bool:
        """Check if the bot is running."""
        return self._running and self._bot is not None

    async def start(self, token: Optional[str] = None):
        """Start the Discord bot."""
        if self.is_running():
            return

        if not token:
            secrets = SecretsManager(settings.SECRETS_DIR)
            token = secrets.get("discord_token")

        if not token:
            raise ValueError("No Discord token provided")

        self._bot = WooSarrBot()
        self._running = True

        try:
            await self._bot.start(token)
        except Exception as e:
            logger.error(f"Bot failed to start: {e}")
            self._running = False
            raise

    async def stop(self):
        """Stop the Discord bot."""
        if not self.is_running():
            return

        self._running = False
        if self._bot:
            await self._bot.close()
            self._bot = None

    async def restart(self, token: Optional[str] = None):
        """Restart the Discord bot."""
        await self.stop()
        await self.start(token)


# Global bot manager instance
bot_manager = BotManager()