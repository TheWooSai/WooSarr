import os

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "woosarr",
        "version": "1.0.0",
        "build_version": os.getenv("BUILD_VERSION", "unknown"),
        "build_date": os.getenv("BUILD_DATE", "unknown"),
    }
