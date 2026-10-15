import os

from app.api import auth, health, libraries, logs, roles, setup, sync, users
from app.core.database import init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="WooSarr", description="Plex ↔ Discord Role Library Sync", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(roles.router, prefix="/api/roles", tags=["roles"])
app.include_router(libraries.router, prefix="/api/libraries", tags=["libraries"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
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
    except Exception as e:
        print(f"Warning: Could not initialize DB: {e}")
