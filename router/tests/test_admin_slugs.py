"""Tests for admin slugs router."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.slug_map import ResourceType, SlugStatus
from app.schemas.slug import SlugMapCreate


@pytest.mark.asyncio
async def test_create_slug_success(async_client: AsyncClient, db: AsyncSession):
    """Test successful slug creation."""
    slug_data = {
        "host": "slotifyme.com",
        "path": "/barbershop-a/downtown",
        "resource_type": "location",
        "resource_id": "loc_456",
        "tenant_id": "ten_123",
        "canonical_url": "https://slotifyme.com/barbershop-a/downtown",
        "status": "active"
    }
    
    response = await async_client.post(
        "/admin/slugs",
        json=slug_data,
        headers={"X-Internal-Role": "admin"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["host"] == slug_data["host"]
    assert data["path"] == slug_data["path"]
    assert data["resource_type"] == slug_data["resource_type"]
    assert data["resource_id"] == slug_data["resource_id"]
    assert data["version"] == 1


@pytest.mark.asyncio
async def test_create_slug_conflict(async_client: AsyncClient, db: AsyncSession):
    """Test slug creation with conflict."""
    slug_data = {
        "host": "slotifyme.com",
        "path": "/barbershop-a/downtown",
        "resource_type": "location",
        "resource_id": "loc_456",
        "tenant_id": "ten_123",
        "canonical_url": "https://slotifyme.com/barbershop-a/downtown",
        "status": "active"
    }
    
    # Create first slug
    response = await async_client.post(
        "/admin/slugs",
        json=slug_data,
        headers={"X-Internal-Role": "admin"}
    )
    assert response.status_code == 201
    
    # Try to create conflicting slug
    response = await async_client.post(
        "/admin/slugs",
        json=slug_data,
        headers={"X-Internal-Role": "admin"}
    )
    
    assert response.status_code == 409
    assert "SLUG_CONFLICT" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_slug_unauthorized(async_client: AsyncClient):
    """Test slug creation without admin role."""
    slug_data = {
        "host": "slotifyme.com",
        "path": "/barbershop-a/downtown",
        "resource_type": "location",
        "resource_id": "loc_456",
        "tenant_id": "ten_123",
        "canonical_url": "https://slotifyme.com/barbershop-a/downtown",
        "status": "active"
    }
    
    response = await async_client.post("/admin/slugs", json=slug_data)
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_slug_success(async_client: AsyncClient, db: AsyncSession):
    """Test successful slug update."""
    # Create slug first
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
    
    # Update slug
    update_data = {
        "canonical_url": "https://slotifyme.com/barbershop-a/downtown-location"
    }
    
    response = await async_client.put(
        f"/admin/slugs/{slug_id}",
        json=update_data,
        headers={"X-Internal-Role": "admin"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["canonical_url"] == update_data["canonical_url"]
    assert data["version"] == 1  # No version bump for non-critical fields


@pytest.mark.asyncio
async def test_delete_slug_soft(async_client: AsyncClient, db: AsyncSession):
    """Test soft delete of slug."""
    # Create slug first
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
    
    # Soft delete
    response = await async_client.delete(
        f"/admin/slugs/{slug_id}?soft=true",
        headers={"X-Internal-Role": "admin"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "deleted"
    assert data["version"] == 2  # Version should be bumped


@pytest.mark.asyncio
async def test_list_slugs(async_client: AsyncClient, db: AsyncSession):
    """Test listing slugs with pagination."""
    # Create multiple slugs
    slugs = [
        {
            "host": "slotifyme.com",
            "path": "/barbershop-a",
            "resource_type": "tenant",
            "resource_id": "ten_123",
            "tenant_id": "ten_123",
            "canonical_url": "https://slotifyme.com/barbershop-a",
            "status": "active"
        },
        {
            "host": "slotifyme.com",
            "path": "/barbershop-a/downtown",
            "resource_type": "location",
            "resource_id": "loc_456",
            "tenant_id": "ten_123",
            "canonical_url": "https://slotifyme.com/barbershop-a/downtown",
            "status": "active"
        }
    ]
    
    for slug_data in slugs:
        await async_client.post(
            "/admin/slugs",
            json=slug_data,
            headers={"X-Internal-Role": "admin"}
        )
    
    # List slugs
    response = await async_client.get(
        "/admin/slugs?host=slotifyme.com&tenant_id=ten_123",
        headers={"X-Internal-Role": "admin"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 20


@pytest.mark.asyncio
async def test_check_availability(async_client: AsyncClient, db: AsyncSession):
    """Test slug availability check."""
    # Create a slug
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
    
    # Check availability of existing slug
    response = await async_client.get(
        "/admin/slugs/check-availability?host=slotifyme.com&path=/barbershop-a/downtown",
        headers={"X-Internal-Role": "admin"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["available"] == False
    assert data["conflicting_id"] is not None
    
    # Check availability of non-existing slug
    response = await async_client.get(
        "/admin/slugs/check-availability?host=slotifyme.com&path=/barbershop-b",
        headers={"X-Internal-Role": "admin"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["available"] == True
    assert data["conflicting_id"] is None
