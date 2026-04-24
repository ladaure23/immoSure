from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl
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

    # FedaPay
    fedapay_secret_key: str = ""
    fedapay_public_key: str = ""
    fedapay_webhook_secret: str = ""
    fedapay_env: Literal["sandbox", "live"] = "sandbox"

    # KKiaPay
    kkiapay_private_key: str = ""
    kkiapay_public_key: str = ""
    kkiapay_secret: str = ""
    kkiapay_sandbox: bool = True

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
    def fedapay_base_url(self) -> str:
        if self.fedapay_env == "live":
            return "https://api.fedapay.com/v1"
        return "https://sandbox-api.fedapay.com/v1"

    @property
    def kkiapay_base_url(self) -> str:
        if self.kkiapay_sandbox:
            return "https://api-sandbox.kkiapay.me"
        return "https://api.kkiapay.me"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()
