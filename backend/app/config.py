from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    BOT_TOKEN: str
    SECRET_KEY: str
    CPA_SECRET_TOKEN: str
    WEBAPP_URL: str = "https://t.me/YourBot/app" # Placeholder or actual URL
    ADMIN_IDS: str = "" # Comma-separated list of Telegram IDs
    
    # Security/ops toggles
    ALLOW_ORIGINS: str = "*"  # Comma-separated list of origins or "*" for all (dev)
    SQL_ECHO: bool = False    # Disable verbose SQL logging by default

    class Config:
        env_file = ".env"

settings = Settings()
