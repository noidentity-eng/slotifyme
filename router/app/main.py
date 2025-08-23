"""Main FastAPI application."""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.cache import close_cache, init_cache
from app.db import close_db, init_db
from app.logging import get_logger, set_request_id
from app.routers import admin_slugs, health, publish, resolve

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Router service")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize cache
    await init_cache()
    logger.info("Cache initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Router service")
    
    # Close cache
    await close_cache()
    logger.info("Cache closed")
    
    # Close database
    await close_db()
    logger.info("Database closed")


# Create FastAPI app
app = FastAPI(
    title="Router/Slug Service",
    description="High-performance URL routing service for Barbershop SaaS",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
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


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests."""
    import uuid
    
    request_id = str(uuid.uuid4())
    set_request_id(request_id)
    
    # Add request ID to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add process time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include routers
app.include_router(health.router)
app.include_router(admin_slugs.router)
app.include_router(resolve.router)
app.include_router(publish.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Router/Slug Service",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
