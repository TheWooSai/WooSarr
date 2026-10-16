import os

from app.api import auth, discord, health, libraries, logs, plex, roles, setup, sync, users
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Setup logging
logger = setup_logging()

app = FastAPI(title="WooSarr", description="Plex ↔ Discord Role Library Sync", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(roles.router, prefix="/api/roles", tags=["roles"])
app.include_router(libraries.router, prefix="/api/libraries", tags=["libraries"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(plex.router, prefix="/api/plex", tags=["plex"])
app.include_router(discord.router, prefix="/api/discord", tags=["discord"])
app.include_router(setup.router, prefix="/api/setup", tags=["setup"])
app.include_router(sync.router, prefix="/api/sync", tags=["sync"])

# Serve static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def serve_frontend():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "WooSarr backend running. Frontend not built."}


@app.on_event("startup")
async def startup():
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize DB: {e}")
