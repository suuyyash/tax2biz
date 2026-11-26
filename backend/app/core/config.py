import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application Settings loaded from environment and .env file.
    All sensitive settings have safe defaults for local demo/development.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Tax2Biz"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8085
    HOST: str = "0.0.0.0"

    # Database: Async SQLite by default, swap with Postgres asyncpg in production
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./tax2biz.db",
        description="Async database connection string"
    )

    # CORS Whitelist (strict origin policy)
    CORS_ORIGINS: str = "http://localhost:8085,http://127.0.0.1:8085,http://localhost:3000,http://127.0.0.1:3000"

    # Modes: "DEMO" or "LIVE"
    PAYMENT_MODE: str = "DEMO"
    NOTIFICATION_MODE: str = "DEMO"

    # Razorpay (Live mode)
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""

    # SMS / WhatsApp Providers (Live mode)
    SMS_PROVIDER: str = "DEMO"
    SMS_API_KEY: str = ""
    WHATSAPP_API_KEY: str = ""

    # TradeMarx Trademark Search API Key
    TRADEMARX_API_KEY: str = "trmx_live_pk_09f3e1a8b74c2d6e5a0198"

    # Security & Tokens
    SECRET_KEY: str = "tax2biz-super-secure-dev-key-change-in-production-random-bytes"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
