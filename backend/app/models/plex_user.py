from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class PlexUser(Base):
    __tablename__ = "plex_users"
    
    id = Column(Integer, primary_key=True, index=True)
    plex_user_id = Column(String(50), unique=True, index=True, nullable=False)
    plex_username = Column(String(100), nullable=False)
    discord_user_id = Column(String(50), ForeignKey("discord_users.discord_user_id"))
    linked_at = Column(Integer)  # Unix timestamp
    
    discord_user = relationship("DiscordUser", back_populates="plex_user")