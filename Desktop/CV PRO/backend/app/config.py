"""Application Configuration - Pydantic Settings"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # App
    APP_NAME: str = "CareerOS AI"
    VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # Database
    DATABASE_URL: str = Field(env="DATABASE_URL")
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # JWT & Security
    SECRET_KEY: str = Field(env="SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_HOURS: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    JWT_REFRESH_EXPIRATION_DAYS: int = Field(default=30, env="JWT_REFRESH_EXPIRATION_DAYS")

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
        ],
        env="CORS_ORIGINS",
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS",
    )

    # LLM APIs
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str = Field(default="", env="ANTHROPIC_API_KEY")
    LLM_PROVIDER: str = Field(default="openai", env="LLM_PROVIDER")  # openai or anthropic

    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/1", env="CELERY_RESULT_BACKEND")

    # AWS
    AWS_ACCESS_KEY_ID: str = Field(default="", env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET: str = Field(default="careeeros-ai", env="AWS_S3_BUCKET")
    AWS_REGION: str = Field(default="eu-west-1", env="AWS_REGION")

    # Email
    SENDGRID_API_KEY: str = Field(default="", env="SENDGRID_API_KEY")
    FROM_EMAIL: str = Field(default="noreply@careeeros.ai", env="FROM_EMAIL")

    # External APIs
    LINKEDIN_ACCESS_TOKEN: str = Field(default="", env="LINKEDIN_ACCESS_TOKEN")
    INDEED_API_KEY: str = Field(default="", env="INDEED_API_KEY")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Features (Feature flags)
    ENABLE_INTERVIEW_COACHING: bool = Field(default=True, env="ENABLE_INTERVIEW_COACHING")
    ENABLE_EMAIL_TRACKING: bool = Field(default=True, env="ENABLE_EMAIL_TRACKING")
    ENABLE_AUTO_RELANCES: bool = Field(default=True, env="ENABLE_AUTO_RELANCES")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance
settings = Settings()
