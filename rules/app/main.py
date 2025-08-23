"""Main FastAPI application for the Rules Service."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import engine, Base
from app.cache import close_redis
from app.routers import (
    health_router,
    admin_plans_router,
    admin_addons_router,
    tenant_plan_router,
    tenant_addons_router,
    tenant_overrides_router,
    overage_pricing_router,
    price_preview_router,
    entitlements_router,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Rules Service...")
    
    # Create database tables (skip in test mode)
    if settings.env != "test":
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Rules Service...")
    await close_redis()
    logger.info("Rules Service shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Rules Service",
    description="Rules Service for Barbershop SaaS - Manages plans, addons, and entitlements",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(admin_plans_router)
app.include_router(admin_addons_router)
app.include_router(tenant_plan_router)
app.include_router(tenant_addons_router)
app.include_router(tenant_overrides_router)
app.include_router(overage_pricing_router)
app.include_router(price_preview_router)
app.include_router(entitlements_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Rules Service API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
