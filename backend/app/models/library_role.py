from app.core.database import Base
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship


class LibraryRole(Base):
    __tablename__ = "library_roles"

    id = Column(Integer, primary_key=True, index=True)
    library_id = Column(Integer, ForeignKey("libraries.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    library = relationship("Library", back_populates="roles")
    role = relationship("Role", back_populates="libraries")
