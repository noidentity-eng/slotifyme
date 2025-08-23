"""Tests for resolve router."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app


@pytest.mark.asyncio
async def test_resolve_success(async_client: AsyncClient, db: AsyncSession):
    """Test successful URL resolution."""
    # Create a slug first
    slug_data = {
        "host": "slotifyme.com",
        "path": "/barbershop-a/downtown",
        "resource_type": "location",
        "resource_id": "loc_456",
        "tenant_id": "ten_123",
        "canonical_url": "https://slotifyme.com/barbershop-a/downtown",
        "status": "active"
    }
    
    await async_client.post(
        "/admin/slugs",
        json=slug_data,
        headers={"X-Internal-Role": "admin"}
    )
    
    # Resolve the URL
    response = await async_client.get(
        "/resolve?host=slotifyme.com&path=/barbershop-a/downtown",
        headers={"X-Internal-Service": "edge"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["match"] == True
    assert data["resource"]["type"] == "location"
    assert data["resource"]["id"] == "loc_456"
    assert data["tenant_id"] == "ten_123"
    assert data["version"] == 1
    assert data["canonical_url"] == "https://slotifyme.com/barbershop-a/downtown"
    assert data["cache"]["max_age"] == 600
    assert "etag" in data["cache"]


@pytest.mark.asyncio
async def test_resolve_not_found(async_client: AsyncClient, db: AsyncSession):
    """Test URL resolution for non-existing slug."""
    response = await async_client.get(
        "/resolve?host=slotifyme.com&path=/non-existing",
        headers={"X-Internal-Service": "edge"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["match"] == False
    assert data["resource"] is None


@pytest.mark.asyncio
async def test_resolve_deleted_slug(async_client: AsyncClient, db: AsyncSession):
    """Test URL resolution for deleted slug."""
    # Create a slug first
    slug_data = {
        "host": "slotifyme.com",
        "path": "/barbershop-a/downtown",
        "resource_type": "location",
        "resource_id": "loc_456",
        "tenant_id": "ten_123",
        "canonical_url": "https://slotifyme.com/barbershop-a/downtown",
        "status": "active"
    }
    
    create_response = await async_client.post(
        "/admin/slugs",
        json=slug_data,
        headers={"X-Internal-Role": "admin"}
    )
    slug_id = create_response.json()["id"]
    
    # Delete the slug
    await async_client.delete(
        f"/admin/slugs/{slug_id}?soft=true",
        headers={"X-Internal-Role": "admin"}
    )
    
    # Try to resolve the deleted slug
    response = await async_client.get(
        "/resolve?host=slotifyme.com&path=/barbershop-a/downtown",
        headers={"X-Internal-Service": "edge"}
    )
    
    assert response.status_code == 410
    assert "deleted" in response.json()["detail"]


@pytest.mark.asyncio
async def test_resolve_unauthorized(async_client: AsyncClient):
    """Test URL resolution without service authentication."""
    response = await async_client.get(
        "/resolve?host=slotifyme.com&path=/barbershop-a/downtown"
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_resolve_cache_hit(async_client: AsyncClient, db: AsyncSession):
    """Test that resolve uses cache on subsequent requests."""
    # Create a slug first
    slug_data = {
        "host": "slotifyme.com",
        "path": "/barbershop-a/downtown",
        "resource_type": "location",
        "resource_id": "loc_456",
        "tenant_id": "ten_123",
        "canonical_url": "https://slotifyme.com/barbershop-a/downtown",
        "status": "active"
    }
    
    await async_client.post(
        "/admin/slugs",
        json=slug_data,
        headers={"X-Internal-Role": "admin"}
    )
    
    # First resolve (should hit database)
    response1 = await async_client.get(
        "/resolve?host=slotifyme.com&path=/barbershop-a/downtown",
        headers={"X-Internal-Service": "edge"}
    )
    
    assert response1.status_code == 200
    
    # Second resolve (should hit cache)
    response2 = await async_client.get(
        "/resolve?host=slotifyme.com&path=/barbershop-a/downtown",
        headers={"X-Internal-Service": "edge"}
    )
    
    assert response2.status_code == 200
    # Both responses should be identical
    assert response1.json() == response2.json()
