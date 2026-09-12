from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Sadangu Sampradayam API"
    app_env: str = "development"
    database_url: str = "sqlite:///./sadangu.db"
    cors_origins: str = "*"

    auth_required: bool = True
    admin_phone: str = "9000000000"
    admin_pin: str = "1234"
    jwt_secret: str = "change-me-in-production"
    token_ttl_minutes: int = 720

    auto_create_schema: bool = True
    seed_demo_data: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.is_production:
            if self.jwt_secret == "change-me-in-production" or len(self.jwt_secret) < 32:
                raise ValueError("JWT_SECRET must be a strong 32+ character value in production")
            if self.admin_pin == "1234":
                raise ValueError("ADMIN_PIN must be changed in production")
            if self.database_url.startswith("sqlite"):
                raise ValueError("Production must use PostgreSQL/Supabase, not SQLite")
            if self.auto_create_schema:
                raise ValueError("AUTO_CREATE_SCHEMA must be false in production; use migrations")
            if self.seed_demo_data:
                raise ValueError("SEED_DEMO_DATA must be false in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
