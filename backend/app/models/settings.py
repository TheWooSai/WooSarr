from sqlalchemy import Column, Integer, String, Boolean, Text
from app.core.database import Base

class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text)
    encrypted = Column(Boolean, default=False)