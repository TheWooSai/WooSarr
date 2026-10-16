from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.core.database import SessionLocal
from app.models.log import LogEntry

router = APIRouter()


class LogEntryResponse(BaseModel):
    id: int
    timestamp: datetime
    level: str
    message: str
    context: Optional[str] = None

    class Config:
        from_attributes = True


class LogsResponse(BaseModel):
    logs: list[LogEntryResponse]
    total: int
    page: int
    page_size: int


@router.get("", response_model=LogsResponse)
def get_logs(
    level: Optional[str] = Query(None, description="Filter by level (INFO, WARN, ERROR)"),
    source: Optional[str] = Query(None, description="Filter by source/logger"),
    start_time: Optional[datetime] = Query(None, description="Filter by start time (ISO 8601)"),
    end_time: Optional[datetime] = Query(None, description="Filter by end time (ISO 8601)"),
    search: Optional[str] = Query(None, description="Search in message"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Page size"),
):
    """Get recent logs with filtering and pagination."""
    db = SessionLocal()
    try:
        query = db.query(LogEntry)

        # Apply filters
        if level:
            query = query.filter(LogEntry.level == level.upper())
        if source:
            query = query.filter(LogEntry.message.like(f"%{source}%"))
        if start_time:
            query = query.filter(LogEntry.timestamp >= start_time)
        if end_time:
            query = query.filter(LogEntry.timestamp <= end_time)
        if search:
            query = query.filter(LogEntry.message.like(f"%{search}%"))

        # Count total
        total = query.count()

        # Order by timestamp descending (newest first)
        query = query.order_by(LogEntry.timestamp.desc())

        # Pagination
        offset = (page - 1) * page_size
        logs = query.offset(offset).limit(page_size).all()

        return LogsResponse(
            logs=[LogEntryResponse(**{
                "id": log.id,
                "timestamp": log.timestamp,
                "level": log.level,
                "message": log.message,
                "context": log.context,
            }) for log in logs],
            total=total,
            page=page,
            page_size=page_size,
        )
    finally:
        db.close()


@router.get("/recent", response_model=list[LogEntryResponse])
def get_recent_logs(limit: int = Query(20, ge=1, le=100)):
    """Get the most recent logs."""
    db = SessionLocal()
    try:
        logs = db.query(LogEntry).order_by(LogEntry.timestamp.desc()).limit(limit).all()
        return [LogEntryResponse(**{
            "id": log.id,
            "timestamp": log.timestamp,
            "level": log.level,
            "message": log.message,
            "context": log.context,
        }) for log in logs]
    finally:
        db.close()
