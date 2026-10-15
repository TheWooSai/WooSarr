"""Test logging system."""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import logging
import tempfile
from pathlib import Path

from app.core.logging import redact, RedactingFormatter, JsonFormatter, setup_logging


def test_redact_token():
    """Test that tokens are redacted."""
    text = "token=abc123token456"
    result = redact(text)
    assert "abc123token456" not in result
    assert "[REDACTED]" in result


def test_redact_api_key():
    """Test that API keys are redacted."""
    text = "api_key=my-secret-key-123"
    result = redact(text)
    assert "my-secret-key-123" not in result
    assert "[REDACTED]" in result


def test_redact_password():
    """Test that passwords are redacted."""
    text = "password=supersecret"
    result = redact(text)
    assert "supersecret" not in result
    assert "[REDACTED]" in result


def test_redact_base64_token():
    """Test that base64 tokens are redacted."""
    text = "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0"
    result = redact(text)
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result
    assert "[REDACTED]" in result


def test_redact_long_number():
    """Test that long numbers (card numbers) are redacted."""
    text = "card=4111111111111111"
    result = redact(text)
    assert "4111111111111111" not in result
    assert "[REDACTED]" in result


def test_redacting_formatter():
    """Test that RedactingFormatter redacts sensitive values."""
    formatter = RedactingFormatter("%(message)s")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="token=secret123",
        args=(),
        exc_info=None,
    )
    result = formatter.format(record)
    assert "secret123" not in result
    assert "[REDACTED]" in result


def test_json_formatter():
    """Test that JsonFormatter produces valid JSON."""
    import json

    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="test message",
        args=(),
        exc_info=None,
    )
    result = formatter.format(record)
    data = json.loads(result)
    assert data["level"] == "INFO"
    assert data["logger"] == "test"
    assert data["message"] == "test message"


def test_setup_logging():
    """Test that setup_logging returns a configured logger."""
    logger = setup_logging()
    assert logger.name == "woosarr"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) >= 1