"""Tests for publish router."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app


@pytest.mark.asyncio
async def test_publish_manifest_success(async_client: AsyncClient, db: AsyncSession):
    """Test successful manifest publishing."""
    # Create some slugs first
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
    
    # Publish manifest
    response = await async_client.post(
        "/publish",
        headers={"X-Internal-Role": "admin"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["items"]) == 2
    assert "generated_at" in data
    
    # Check that items are in compact format
    for item in data["items"]:
        assert len(item) == 5  # [host, path, resource_type, resource_id, version]
        assert isinstance(item[0], str)  # host
        assert isinstance(item[1], str)  # path
        assert isinstance(item[2], str)  # resource_type
        assert isinstance(item[3], str)  # resource_id
        assert isinstance(item[4], int)  # version


@pytest.mark.asyncio
async def test_publish_manifest_empty(async_client: AsyncClient, db: AsyncSession):
    """Test manifest publishing with no active slugs."""
    response = await async_client.post(
        "/publish",
        headers={"X-Internal-Role": "admin"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert len(data["items"]) == 0
    assert "generated_at" in data


@pytest.mark.asyncio
async def test_publish_manifest_unauthorized(async_client: AsyncClient):
    """Test manifest publishing without admin role."""
    response = await async_client.post("/publish")
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_publish_manifest_internal(async_client: AsyncClient, db: AsyncSession):
    """Test manifest publishing with internal service authentication."""
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
    
    # Publish manifest with internal service auth
    response = await async_client.post(
        "/publish/internal",
        headers={"X-Internal-Service": "edge"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_publish_manifest_excludes_inactive(async_client: AsyncClient, db: AsyncSession):
    """Test that manifest only includes active slugs."""
    # Create active slug
    active_slug = {
        "host": "slotifyme.com",
        "path": "/barbershop-a",
        "resource_type": "tenant",
        "resource_id": "ten_123",
        "tenant_id": "ten_123",
        "canonical_url": "https://slotifyme.com/barbershop-a",
        "status": "active"
    }
    
    create_response = await async_client.post(
        "/admin/slugs",
        json=active_slug,
        headers={"X-Internal-Role": "admin"}
    )
    slug_id = create_response.json()["id"]
    
    # Create draft slug
    draft_slug = {
        "host": "slotifyme.com",
        "path": "/barbershop-b",
        "resource_type": "tenant",
        "resource_id": "ten_456",
        "tenant_id": "ten_456",
        "canonical_url": "https://slotifyme.com/barbershop-b",
        "status": "draft"
    }
    
    await async_client.post(
        "/admin/slugs",
        json=draft_slug,
        headers={"X-Internal-Role": "admin"}
    )
    
    # Publish manifest
    response = await async_client.post(
        "/publish",
        headers={"X-Internal-Role": "admin"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1  # Only active slug should be included
    assert len(data["items"]) == 1
    assert data["items"][0][1] == "/barbershop-a"  # Active slug path
