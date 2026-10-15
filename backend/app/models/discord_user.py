from app.core.database import Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


class DiscordUser(Base):
    __tablename__ = "discord_users"

    discord_user_id = Column(String(50), primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    discriminator = Column(String(5), default="0")

    plex_user = relationship("PlexUser", back_populates="discord_user", uselist=False)
