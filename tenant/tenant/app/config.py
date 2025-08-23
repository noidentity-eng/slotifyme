"""Configuration settings for the tenant service."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/tenant",
        description="PostgreSQL database URL"
    )
    
    # Redis (for idempotency)
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL for idempotency storage"
    )
    
    # Security
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    
    # Rules service (optional)
    rules_base_url: Optional[str] = Field(
        default=None,
        description="Base URL for rules service (optional)"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    # Service
    service_name: str = Field(
        default="tenant",
        description="Service name for internal headers"
    )
    
    # Idempotency
    idempotency_ttl_hours: int = Field(
        default=24,
        description="TTL for idempotency keys in hours"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
