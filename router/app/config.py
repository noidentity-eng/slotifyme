"""Configuration settings for the Router service."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = Field(..., description="PostgreSQL connection string")
    
    # Redis (optional)
    redis_url: Optional[str] = Field(None, description="Redis connection string")
    
    # External services
    tenant_base_url: Optional[str] = Field(None, description="Tenant service base URL")
    
    # S3 for manifest publishing
    publish_s3_bucket: Optional[str] = Field(None, description="S3 bucket for manifest uploads")
    
    # Application
    log_level: str = Field("INFO", description="Logging level")
    debug: bool = Field(False, description="Debug mode")
    
    # Cache settings
    cache_ttl: int = Field(600, description="Cache TTL in seconds (5-15 minutes)")
    
    # Pagination
    default_page_size: int = Field(20, description="Default page size for pagination")
    max_page_size: int = Field(100, description="Maximum page size for pagination")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
