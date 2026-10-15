"""Configuration loader for WooSarr.

Reads from environment variables (WOOSARR_ prefix) and /config directory.
No secrets in env defaults - all secrets must be provided via /config volume.
"""
import json
import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Environment variables use WOOSARR_ prefix.
    Config file at /config/settings.json overrides env vars.
    """

    model_config = SettingsConfigDict(
        env_prefix="WOOSARR_",
        env_file=".env",
        extra="ignore",
    )

    # Paths
    CONFIG_DIR: Path = Path("/config")
    DB_PATH: Path = Path("/config/woosarr.db")
    SECRETS_DIR: Path = Path("/config/secrets")
    MASTER_KEY_PATH: Path = Path("/config/secrets/master.key")
    LOG_DIR: Path = Path("/config/logs")

    # Discord
    DISCORD_BOT_TOKEN: str = ""
    DISCORD_GUILD_ID: int = 0

    # Plex
    PLEX_SERVER_URL: str = ""
    PLEX_TOKEN: str = ""

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 2000

    # Logging
    LOG_LEVEL: str = "INFO"

    # Bot
    BOT_PREFIX: str = "!"

    def load_config_file(self) -> None:
        """Load settings from /config/settings.json if it exists."""
        config_file = self.CONFIG_DIR / "settings.json"
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                # Update settings from config file
                for key, value in config.items():
                    attr_name = key.upper()
                    if hasattr(self, attr_name):
                        setattr(self, attr_name, value)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file {config_file}: {e}")


settings = Settings()
settings.load_config_file()
