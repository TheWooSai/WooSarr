from fastapi import APIRouter

from app.core.logging import setup_logging

router = APIRouter()
logger = setup_logging()


@router.post("/now")
def sync_now():
    """Trigger a manual sync for all users."""
    # TODO: Implement sync logic
    logger.info("Manual sync triggered")
    return {"success": True, "message": "Sync triggered"}


@router.post("/now/user/{user_id}")
def sync_user(user_id: str):
    """Trigger a manual sync for a specific user."""
    # TODO: Implement sync logic
    logger.info(f"Manual sync triggered for user {user_id}")
    return {"success": True, "message": f"Sync triggered for user {user_id}"}
