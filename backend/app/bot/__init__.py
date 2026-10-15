"""WooSarr Discord bot skeleton."""
import discord
from discord.ext import commands

from app.core.config import settings


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