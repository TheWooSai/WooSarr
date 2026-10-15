from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(
    f"sqlite:///{settings.DB_PATH}",
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    settings.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    settings.SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)