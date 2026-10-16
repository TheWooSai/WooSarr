"""Plex API endpoints."""

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.secrets import SecretsManager
from app.services.plex_api_gateway import PlexApiGateway

router = APIRouter()
logger = setup_logging()

# In-memory state for OAuth flow
_oauth_state = {}


class PlexAuthRequest(BaseModel):
    """Request model for Plex authentication."""
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None


class PlexAuthResponse(BaseModel):
    """Response model for Plex authentication."""
    success: bool
    message: str
    server_name: Optional[str] = None
    machine_identifier: Optional[str] = None


class PlexOAuthStartRequest(BaseModel):
    """Request model for starting Plex OAuth flow."""
    pass


class PlexOAuthStartResponse(BaseModel):
    """Response model for starting Plex OAuth flow."""
    success: bool
    code: str
    url: str
    message: str


class PlexOAuthPollRequest(BaseModel):
    """Request model for polling Plex OAuth flow."""
    code: str


class PlexOAuthPollResponse(BaseModel):
    """Response model for polling Plex OAuth flow."""
    success: bool
    authenticated: bool
    token: Optional[str] = None
    server_name: Optional[str] = None
    machine_identifier: Optional[str] = None
    message: str


@router.post("/auth", response_model=PlexAuthResponse)
def authenticate(request: PlexAuthRequest):
    """Authenticate with Plex using username/password or token."""
    gateway = PlexApiGateway(settings.PLEX_SERVER_URL)

    if request.token:
        success = gateway.authenticate_with_token(request.token)
        if success:
            # Store token encrypted
            secrets = SecretsManager(settings.SECRETS_DIR)
            secrets.set("plex_token", request.token)

            server_info = gateway.get_server_info()
            return PlexAuthResponse(
                success=True,
                message="Authenticated successfully",
                server_name=server_info.friendly_name,
                machine_identifier=server_info.machine_identifier,
            )
        else:
            return PlexAuthResponse(success=False, message="Invalid token")
    elif request.username and request.password:
        success = gateway.authenticate(request.username, request.password)
        if success:
            token = gateway.get_auth_token()
            # Store token encrypted
            secrets = SecretsManager(settings.SECRETS_DIR)
            secrets.set("plex_token", token)

            server_info = gateway.get_server_info()
            return PlexAuthResponse(
                success=True,
                message="Authenticated successfully",
                server_name=server_info.friendly_name,
                machine_identifier=server_info.machine_identifier,
            )
        else:
            return PlexAuthResponse(success=False, message="Invalid credentials")
    else:
        return PlexAuthResponse(success=False, message="Missing credentials")


@router.post("/oauth/start", response_model=PlexOAuthStartResponse)
def oauth_start(request: PlexOAuthStartRequest):
    """Start the Plex OAuth flow."""
    try:
        from plexapi.myplex import MyPlexPinLogin

        pin = MyPlexPinLogin(oauth=True)
        _oauth_state[pin.code] = pin

        return PlexOAuthStartResponse(
            success=True,
            code=pin.code,
            url=pin.url,
            message="OAuth flow started. Open the URL in your browser.",
        )
    except Exception as e:
        logger.error(f"Failed to start OAuth flow: {e}")
        return PlexOAuthStartResponse(
            success=False,
            code="",
            url="",
            message=f"Failed to start OAuth flow: {e}",
        )


@router.post("/oauth/poll", response_model=PlexOAuthPollResponse)
def oauth_poll(request: PlexOAuthPollRequest):
    """Poll the Plex OAuth flow for completion."""
    pin = _oauth_state.get(request.code)
    if not pin:
        return PlexOAuthPollResponse(
            success=False,
            authenticated=False,
            message="Invalid or expired code",
        )

    try:
        pin.check()
        if pin.authenticated:
            # Store token encrypted
            secrets = SecretsManager(settings.SECRETS_DIR)
            secrets.set("plex_token", pin.token)

            # Clean up state
            del _oauth_state[request.code]

            # Get server info
            gateway = PlexApiGateway(settings.PLEX_SERVER_URL, pin.token)
            server_info = gateway.get_server_info()

            return PlexOAuthPollResponse(
                success=True,
                authenticated=True,
                token=pin.token,
                server_name=server_info.friendly_name,
                machine_identifier=server_info.machine_identifier,
                message="OAuth flow completed successfully",
            )
        else:
            return PlexOAuthPollResponse(
                success=True,
                authenticated=False,
                message="Waiting for user to authenticate",
            )
    except Exception as e:
        logger.error(f"Failed to poll OAuth flow: {e}")
        return PlexOAuthPollResponse(
            success=False,
            authenticated=False,
            message=f"Failed to poll OAuth flow: {e}",
        )


@router.get("/status")
def get_status():
    """Get Plex connection status."""
    secrets = SecretsManager(settings.SECRETS_DIR)
    token = secrets.get("plex_token")

    if not token:
        return {"authenticated": False, "message": "Not authenticated"}

    gateway = PlexApiGateway(settings.PLEX_SERVER_URL, token)
    if gateway.is_authenticated():
        server_info = gateway.get_server_info()
        return {
            "authenticated": True,
            "server_name": server_info.friendly_name,
            "machine_identifier": server_info.machine_identifier,
        }
    else:
        return {"authenticated": False, "message": "Token invalid or expired"}