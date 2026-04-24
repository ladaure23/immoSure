from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_url: str = "http://localhost:8000"
    environment: Literal["development", "production", "test"] = "development"
    secret_key: str
    access_token_expire_minutes: int = 60

    # Database
    database_url: str

    # MTN Mobile Money
    mtn_subscription_key: str = ""
    mtn_api_user: str = ""
    mtn_api_key: str = ""
    mtn_env: str = "sandbox"

    # Telegram
    telegram_bot_token: str = ""

    # Anthropic
    anthropic_api_key: str = ""

    # Storage
    upload_dir: str = "/uploads/receipts"

    # Scheduler
    scheduler_timezone: str = "Africa/Porto-Novo"
    notification_hour: int = 9
    notification_minute: int = 0

    @property
    def mtn_base_url(self) -> str:
        if self.mtn_env == "sandbox":
            return "https://sandbox.momodeveloper.mtn.com"
        return "https://proxy.momoapi.mtn.com"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()
