"""Configuration module for Taller 3 application."""
import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""

    APP_NAME: str = "Dashboard Taller 3 - Modo Oscuro"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # ConfigCat SDK Key (configured in Render or .env)
    # If empty or not set, the app runs in local simulation mode
    CONFIGCAT_SDK_KEY: Optional[str] = os.getenv("CONFIGCAT_SDK_KEY", "").strip() or None

    # Default simulation stage when ConfigCat SDK Key is not provided:
    # 'ticket_1': Flag dark_mode_enabled OFF (0% rollout)
    # 'ticket_2': Flag dark_mode_enabled 10% Canary rollout (visible only to 10% of users)
    # 'ticket_3': Flag dark_mode_enabled 100% ON (all users + persistence)
    DEFAULT_STAGE: str = os.getenv("FEATURE_STAGE", "ticket_1").lower()

    # Host & Port (Render injects PORT)
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")


settings = Settings()
