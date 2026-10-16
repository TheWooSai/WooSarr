"""Authentication API endpoints."""

from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.secrets import SecretsManager

router = APIRouter()
logger = setup_logging()

# In-memory user store (TODO: replace with database)
_users = {}
_tokens = {}


class UserCreate(BaseModel):
    """Request model for creating a user."""
    username: str
    password: str
    is_admin: bool = False


class UserLogin(BaseModel):
    """Request model for logging in."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Response model for token."""
    access_token: str
    token_type: str = "bearer"


@router.post("/register")
def register(user: UserCreate):
    """Register a new user."""
    if user.username in _users:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash password (TODO: use proper hashing)
    _users[user.username] = {
        "password": user.password,
        "is_admin": user.is_admin,
    }

    return {"success": True, "message": "User registered"}


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin):
    """Log in and get a token."""
    if user.username not in _users:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if _users[user.username]["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate token (TODO: use proper JWT)
    import uuid
    token = str(uuid.uuid4())
    _tokens[token] = {
        "username": user.username,
        "expires": datetime.now() + timedelta(hours=24),
    }

    return TokenResponse(access_token=token)


@router.get("/me")
def get_me(token: str):
    """Get current user info."""
    if token not in _tokens:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_info = _tokens[token]
    if user_info["expires"] < datetime.now():
        raise HTTPException(status_code=401, detail="Token expired")

    return {
        "username": user_info["username"],
        "is_admin": _users[user_info["username"]]["is_admin"],
    }
