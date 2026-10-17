from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.core.secrets import SecretsManager

router = APIRouter()


@router.get("/status")
async def get_setup_status():
    """Get the status of Plex and Discord setup."""
    secrets = SecretsManager(settings.SECRETS_DIR)

    # Check Plex status
    plex_authenticated = False
    plex_server_name = ""
    try:
        from app.services.plex_gateway import PlexApiGateway
        gateway = PlexApiGateway()
        if gateway.is_authenticated():
            plex_authenticated = True
            server_info = gateway.get_server_info()
            plex_server_name = server_info.friendly_name
    except Exception:
        pass

    # Check Discord status
    discord_running = False
    try:
        from app.bot import bot_manager
        discord_running = bot_manager.is_running()
    except Exception:
        pass

    return {
        "plex": {
            "authenticated": plex_authenticated,
            "server_name": plex_server_name,
        },
        "discord": {
            "running": discord_running,
        },
    }


@router.post("/plex/authenticate")
async def setup_plex_authenticate():
    """Start Plex OAuth flow."""
    from app.api.plex import start_oauth

    try:
        result = await start_oauth()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plex/poll")
async def setup_plex_poll(code: str):
    """Poll Plex OAuth status."""
    from app.api.plex import poll_oauth

    try:
        result = await poll_oauth(code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/discord/token")
async def setup_discord_token(token: str):
    """Save Discord bot token."""
    secrets = SecretsManager(settings.SECRETS_DIR)
    secrets.set("discord_token", token)

    # Start the bot
    try:
        from app.bot import bot_manager
        await bot_manager.start(token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"success": True}
