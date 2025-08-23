"""Configuration settings for the Rules Service."""

import os
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    env: str = Field(default="development", env="ENV")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Database
    database_url: str = Field(
        default="postgresql+psycopg://barbershop_admin:d*Kq.I.|eVLlg*k6h-_6v.X-M4cF@barbershop-db.c58weuo0ic5q.us-west-2.rds.amazonaws.com:5432/barbershop",
        env="DATABASE_URL"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://redis:6379/0",
        env="REDIS_URL"
    )
    
    # Cache settings
    cache_ttl_seconds: int = Field(default=900, env="CACHE_TTL_SECONDS")
    
    # Pricing service
    pricing_base_url: Optional[str] = Field(default=None, env="PRICING_BASE_URL")
    
    # Auth settings
    admin_role_header: str = Field(default="X-Internal-Role", env="ADMIN_ROLE_HEADER")
    internal_service_header: str = Field(
        default="X-Internal-Service", 
        env="INTERNAL_SERVICE_HEADER"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
