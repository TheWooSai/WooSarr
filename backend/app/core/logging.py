"""Logging system for WooSarr.

Structured logging with redaction of sensitive values,
persistent storage to DB and rotating file, queryable/streamable.
"""
import json
import logging
import os
import re
import shutil
import threading
from datetime import datetime
from logging import FileHandler, Formatter, Handler
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.log import LogEntry

# Pattern to match common secret/token formats
SECRET_PATTERNS = [
    re.compile(r"(?i)(token|api[_-]?key|secret|password)[=:]\s*([^\s]+)"),
    re.compile(r"[A-Za-z0-9+/]{20,}={0,2}"),  # Base64 tokens
    re.compile(r"\b\d{16,}\b"),  # Long numbers (card numbers, etc.)
]

REDACTED = "[REDACTED]"


def redact(text: str) -> str:
    """Redact sensitive values from text."""
    # Redact key=value patterns (token=, api_key=, secret=, password=)
    text = re.sub(
        r"(?i)(token|api[_-]?key|secret|password)[=:]\s*\S+",
        r"\1=" + REDACTED,
        text,
    )
    # Redact base64 tokens (long base64 strings)
    text = re.sub(r"[A-Za-z0-9+/]{20,}={0,2}", REDACTED, text)
    # Redact long numbers (card numbers, etc.)
    text = re.sub(r"\b\d{16,}\b", REDACTED, text)
    return text


class RedactingFormatter(Formatter):
    """Log formatter that redacts sensitive values."""

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        return redact(message)


class JsonFormatter(Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data

        # Redact sensitive values
        log_entry["message"] = redact(log_entry["message"])

        return json.dumps(log_entry)


class DBLogHandler(Handler):
    """Log handler that stores logs in the database."""

    def __init__(self) -> None:
        super().__init__()
        self.setFormatter(JsonFormatter())

    def emit(self, record: logging.LogRecord) -> None:
        try:
            log_entry = LogEntry(
                timestamp=datetime.fromtimestamp(record.created),
                level=record.levelname,
                logger=record.name,
                message=record.getMessage(),
                module=record.module,
                function=record.funcName,
                line=record.lineno,
            )

            db = SessionLocal()
            try:
                db.add(log_entry)
                db.commit()
            finally:
                db.close()
        except Exception:
            self.handleError(record)


class RotatingFileHandler(FileHandler):
    """Rotating file handler that creates the log directory if needed."""

    def __init__(self, filename: str, max_bytes: int = 10_000_000, backup_count: int = 5) -> None:
        # Ensure log directory exists
        log_dir = Path(filename).parent
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

        super().__init__(filename, mode="a", encoding="utf-8")
        self.max_bytes = max_bytes
        self.backup_count = backup_count

    def doRoll(self) -> None:
        """Rotate log files."""
        self.close()

        # Remove oldest backup
        oldest = f"{self.baseFilename}.{self.backup_count}"
        if os.path.exists(oldest):
            os.remove(oldest)

        # Shift backups
        for i in range(self.backup_count - 1, 0, -1):
            src = f"{self.baseFilename}.{i}"
            dst = f"{self.baseFilename}.{i + 1}"
            if os.path.exists(src):
                shutil.move(src, dst)

        # Move current to .1
        shutil.move(self.baseFilename, f"{self.baseFilename}.1")

        # Reopen
        self.stream = open(self.baseFilename, "a", encoding="utf-8")

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record, rotating if needed."""
        try:
            msg = self.format(record)
            if self.stream.tell() + len(msg) > self.max_bytes:
                self.doRoll()
            self.stream.write(msg + self.terminator)
            self.stream.flush()
        except Exception:
            self.handleError(record)


def setup_logging() -> logging.Logger:
    """Configure and return the application logger."""
    logger = logging.getLogger("woosarr")
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler (redacted)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(RedactingFormatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(console_handler)

    # File handler (rotating, redacted)
    try:
        file_handler = RotatingFileHandler(
            str(settings.LOG_DIR / "woosarr.log"),
            max_bytes=10_000_000,
            backup_count=5,
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(RedactingFormatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        logger.addHandler(file_handler)
    except OSError:
        pass  # Log directory may not be writable

    # DB handler
    try:
        db_handler = DBLogHandler()
        db_handler.setLevel(logging.INFO)
        logger.addHandler(db_handler)
    except Exception:
        pass  # DB may not be initialized yet

    return logger
    return text