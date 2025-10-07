"""Configuration management for MediaRouter backend."""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
from typing import Union


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "sqlite:///./storage/db.sqlite"

    # Storage
    storage_path: str = "./storage/videos"
    temp_path: str = "./storage/temp"

    # Server
    port: int = 3001
    host: str = "0.0.0.0"
    frontend_url: str = "http://localhost:3000"

    # Security
    encryption_key: str = "change-this-encryption-key"
    secret_key: str = "change-this-secret-key"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # CORS
    cors_origins: Union[list[str], str] = "http://localhost:3000,http://localhost:5173"

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
