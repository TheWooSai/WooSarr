"""Discord API endpoints."""

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.bot import bot_manager
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.secrets import SecretsManager

router = APIRouter()
logger = setup_logging()


class DiscordTokenRequest(BaseModel):
    """Request model for Discord token."""
    token: str


class DiscordStatusResponse(BaseModel):
    """Response model for Discord status."""
    running: bool
    user: Optional[str] = None


@router.get("/status", response_model=DiscordStatusResponse)
def get_status():
    """Get Discord bot status."""
    if bot_manager.is_running():
        return DiscordStatusResponse(
            running=True,
            user=str(bot_manager._bot.user) if bot_manager._bot and bot_manager._bot.user else None,
        )
    return DiscordStatusResponse(running=False)


@router.post("/start")
async def start_bot(request: Optional[DiscordTokenRequest] = None):
    """Start the Discord bot."""
    try:
        token = request.token if request else None
        await bot_manager.start(token)
        return {"success": True, "message": "Bot started"}
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        return {"success": False, "message": str(e)}


@router.post("/stop")
async def stop_bot():
    """Stop the Discord bot."""
    try:
        await bot_manager.stop()
        return {"success": True, "message": "Bot stopped"}
    except Exception as e:
        logger.error(f"Failed to stop bot: {e}")
        return {"success": False, "message": str(e)}


@router.post("/restart")
async def restart_bot(request: Optional[DiscordTokenRequest] = None):
    """Restart the Discord bot."""
    try:
        token = request.token if request else None
        await bot_manager.restart(token)
        return {"success": True, "message": "Bot restarted"}
    except Exception as e:
        logger.error(f"Failed to restart bot: {e}")
        return {"success": False, "message": str(e)}


@router.post("/token")
def set_token(request: DiscordTokenRequest):
    """Set the Discord bot token."""
    secrets = SecretsManager(settings.SECRETS_DIR)
    secrets.set("discord_token", request.token)
    return {"success": True, "message": "Token saved"}


@router.get("/guilds")
def list_guilds():
    """List all guilds the bot is in."""
    if not bot_manager.is_running() or not bot_manager._bot:
        return {"guilds": []}

    guilds = []
    for guild in bot_manager._bot.guilds:
        guilds.append({
            "id": str(guild.id),
            "name": guild.name,
        })
    return {"guilds": guilds}


@router.post("/guilds/select")
def select_guild(guild_id: str):
    """Select a guild to manage."""
    secrets = SecretsManager(settings.SECRETS_DIR)
    secrets.set("discord_guild_id", guild_id)
    return {"success": True, "message": "Guild selected"}


@router.get("/roles")
def list_roles():
    """List all roles in the selected guild."""
    secrets = SecretsManager(settings.SECRETS_DIR)
    guild_id = secrets.get("discord_guild_id")

    if not guild_id or not bot_manager.is_running() or not bot_manager._bot:
        return {"roles": []}

    guild = bot_manager._bot.get_guild(int(guild_id))
    if not guild:
        return {"roles": []}

    roles = []
    for role in guild.roles:
        roles.append({
            "id": str(role.id),
            "name": role.name,
            "color": str(role.color),
            "position": role.position,
        })
    return {"roles": roles}


@router.get("/members")
def list_members():
    """List all members in the selected guild."""
    secrets = SecretsManager(settings.SECRETS_DIR)
    guild_id = secrets.get("discord_guild_id")

    if not guild_id or not bot_manager.is_running() or not bot_manager._bot:
        return {"members": []}

    guild = bot_manager._bot.get_guild(int(guild_id))
    if not guild:
        return {"members": []}

    members = []
    for member in guild.members:
        members.append({
            "id": str(member.id),
            "display_name": member.display_name,
            "role_ids": [str(role.id) for role in member.roles],
        })
    return {"members": members}