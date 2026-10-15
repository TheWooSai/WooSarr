from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CONFIG_DIR: Path = Path("/config")
    DB_PATH: Path = Path("/config/woosarr.db")
    SECRETS_DIR: Path = Path("/config/secrets")
    MASTER_KEY_PATH: Path = Path("/config/secrets/master.key")

    # Discord
    DISCORD_BOT_TOKEN: str = ""
    DISCORD_GUILD_ID: int = 0

    # Plex
    PLEX_SERVER_URL: str = ""
    PLEX_TOKEN: str = ""

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 2000

    class Config:
        env_prefix = "WOOSARR_"


settings = Settings()
