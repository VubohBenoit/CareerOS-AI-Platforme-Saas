from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "DeafHire API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "deafhire-dev-secret-change-in-production"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:3000", "*"]

    # Sign Language Model
    SIGN_MODEL_PATH: str = "../ml/model/lsf_model.pkl"

    # SMTP — leave empty to use demo/log mode
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_TLS: bool = True
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@deafhire.fr"

    # Session
    SESSION_TTL_SECONDS: int = 3600

    class Config:
        env_file = ".env"
        extra = "ignore"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str) and value.lower() in {"release", "prod", "production"}:
            return False
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
