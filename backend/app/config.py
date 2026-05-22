from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_url: str = "http://localhost:8000"
    environment: Literal["development", "production", "test"] = "development"
    secret_key: str
    access_token_expire_minutes: int = 60

    # Database
    database_url: str

    # FedaPay Marketplace
    fedapay_secret_key: str = ""
    fedapay_webhook_secret: str = ""
    fedapay_env: Literal["sandbox", "production"] = "sandbox"
    fedapay_platform_account_ref: str = ""

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
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()
