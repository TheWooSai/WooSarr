from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    discord_role_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    color = Column(Integer, default=0)
    is_exempt = Column(Boolean, default=False)
    
    libraries = relationship("LibraryRole", back_populates="role")