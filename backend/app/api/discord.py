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