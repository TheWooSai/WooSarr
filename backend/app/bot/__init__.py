"""WooSarr Discord bot skeleton."""
import asyncio
import discord
from discord.ext import commands

from app.core.config import settings
from app.core.logging import setup_logging

logger = setup_logging()


class WooSarrBot(commands.Bot):
    """WooSarr Discord bot with slash commands."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix=settings.BOT_PREFIX,
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self) -> None:
        """Initialize bot commands and sync slash commands."""
        # Sync slash commands to all guilds
        synced = await self.tree.sync()
        print(f"Synced {len(synced)} slash commands")

    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        print(f"Logged in as {self.user} (ID: {self.user.id})")


class BotManager:
    """Manages the lifecycle of the Discord bot."""

    def __init__(self) -> None:
        self._bot: WooSarrBot | None = None
        self._task: asyncio.Task | None = None

    @property
    def bot(self) -> WooSarrBot | None:
        """Get the bot instance."""
        return self._bot

    def is_running(self) -> bool:
        """Check if the bot is running."""
        return self._task is not None and not self._task.done()

    async def start(self, token: str | None = None) -> None:
        """Start the Discord bot."""
        if self.is_running():
            return

        self._bot = WooSarrBot()

        # Register ping command
        @self._bot.tree.command(name="ping", description="Check if the bot is alive")
        async def ping(interaction: discord.Interaction) -> None:
            await interaction.response.send_message("Pong!")

        async def run_bot() -> None:
            try:
                await self._bot.start(token or settings.DISCORD_BOT_TOKEN)
            except Exception as e:
                logger.error(f"Bot error: {e}")

        self._task = asyncio.create_task(run_bot())

    async def stop(self) -> None:
        """Stop the Discord bot."""
        if self._bot:
            await self._bot.close()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._bot = None
        self._task = None

    async def restart(self, token: str | None = None) -> None:
        """Restart the Discord bot."""
        await self.stop()
        await self.start(token)


# Singleton bot manager
bot_manager = BotManager()


def create_bot() -> WooSarrBot:
    """Factory function to create a WooSarrBot instance."""
    return WooSarrBot()


def run_bot() -> None:
    """Run the bot with the configured token."""
    bot = create_bot()

    # Register ping command
    @bot.tree.command(name="ping", description="Check if the bot is alive")
    async def ping(interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Pong!")

    bot.run(settings.DISCORD_BOT_TOKEN)