from datetime import datetime

from app.core.database import Base
from sqlalchemy import Column, DateTime, Integer, String, Text


class LogEntry(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String(10), default="INFO")  # INFO, WARN, ERROR
    message = Column(Text, nullable=False)
    context = Column(Text)  # JSON string for additional context
