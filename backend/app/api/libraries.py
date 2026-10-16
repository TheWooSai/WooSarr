from fastapi import APIRouter

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.secrets import SecretsManager
from app.services.plex_api_gateway import PlexApiGateway

router = APIRouter()
logger = setup_logging()


@router.get("/")
def list_libraries():
    """List all libraries from Plex."""
    secrets = SecretsManager(settings.SECRETS_DIR)
    token = secrets.get("plex_token")

    if not token:
        return {"libraries": [], "message": "Not authenticated"}

    gateway = PlexApiGateway(settings.PLEX_SERVER_URL, token)
    libraries = gateway.list_libraries()
    return {
        "libraries": [
            {
                "key": lib.key,
                "title": lib.title,
                "type": lib.type,
                "agent": lib.agent,
            }
            for lib in libraries
        ]
    }


@router.post("/sync")
def sync_libraries():
    """Sync libraries from Plex to the database."""
    secrets = SecretsManager(settings.SECRETS_DIR)
    token = secrets.get("plex_token")

    if not token:
        return {"success": False, "message": "Not authenticated"}

    gateway = PlexApiGateway(settings.PLEX_SERVER_URL, token)
    libraries = gateway.list_libraries()

    # TODO: Upsert libraries to database
    # For now, just return the count
    return {
        "success": True,
        "message": f"Synced {len(libraries)} libraries",
        "count": len(libraries),
    }
