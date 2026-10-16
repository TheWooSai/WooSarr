from fastapi import APIRouter

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.secrets import SecretsManager
from app.services.plex_api_gateway import PlexApiGateway

router = APIRouter()
logger = setup_logging()


@router.get("/")
def list_users():
    """List all users with access to the Plex server."""
    secrets = SecretsManager(settings.SECRETS_DIR)
    token = secrets.get("plex_token")

    if not token:
        return {"users": [], "message": "Not authenticated"}

    gateway = PlexApiGateway(settings.PLEX_SERVER_URL, token)
    users = gateway.list_users()
    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "thumb": user.thumb,
                "is_home_user": user.is_home_user,
                "is_restricted": user.is_restricted,
            }
            for user in users
        ]
    }


@router.post("/sync")
def sync_users():
    """Sync users from Plex to the database."""
    secrets = SecretsManager(settings.SECRETS_DIR)
    token = secrets.get("plex_token")

    if not token:
        return {"success": False, "message": "Not authenticated"}

    gateway = PlexApiGateway(settings.PLEX_SERVER_URL, token)
    users = gateway.list_users()

    # TODO: Upsert users to database
    # For now, just return the count
    return {
        "success": True,
        "message": f"Synced {len(users)} users",
        "count": len(users),
    }
