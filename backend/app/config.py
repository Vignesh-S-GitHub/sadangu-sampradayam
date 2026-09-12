import os
from functools import lru_cache


class Settings:
    def __init__(self):
        self.app_name = "Sadangu Sampradayam API"
        self.db_dsn = os.getenv("SADANGU_DB_DSN", "sqlite:///./sadangu.db")
        self.cors_origins = os.getenv("SADANGU_CORS", "*")

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
