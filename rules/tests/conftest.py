"""Pytest configuration and fixtures."""

import pytest
import asyncio
import os
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import Base, get_db
from app.config import settings


# Test database - use SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client() -> Generator:
    """Create test client."""
    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Override settings for testing
    original_database_url = settings.database_url
    original_env = settings.env
    settings.database_url = SQLALCHEMY_DATABASE_URL
    settings.env = "test"
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as c:
        yield c
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    
    # Restore original settings
    settings.database_url = original_database_url
    settings.env = original_env


@pytest.fixture(autouse=True)
def db_session():
    """Get database session for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up database after each test
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)


@pytest.fixture
def admin_headers():
    """Admin headers for testing."""
    return {"X-Internal-Role": "admin"}


@pytest.fixture
def internal_headers():
    """Internal service headers for testing."""
    return {"X-Internal-Service": "test-service"}
