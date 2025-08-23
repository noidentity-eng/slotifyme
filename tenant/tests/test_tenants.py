"""Tests for tenant endpoints."""

import pytest
from fastapi.testclient import TestClient
from tenant.app.models.tenant import TenantStatus


def test_create_tenant_success(client: TestClient, admin_headers: dict, idempotency_key: str):
    """Test successful tenant creation."""
    tenant_data = {
        "name": "Test Barbershop",
        "slug": "test-barbershop"
    }
    
    headers = {**admin_headers, "Idempotency-Key": idempotency_key}
    
    response = client.post("/tenants", json=tenant_data, headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Barbershop"
    assert data["slug"] == "test-barbershop"
    assert "tenant_id" in data


def test_create_tenant_without_idempotency_key(client: TestClient, admin_headers: dict):
    """Test tenant creation without idempotency key fails."""
    tenant_data = {
        "name": "Test Barbershop",
        "slug": "test-barbershop"
    }
    
    response = client.post("/tenants", json=tenant_data, headers=admin_headers)
    
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "IDEMPOTENCY_KEY_REQUIRED"


def test_create_tenant_without_admin_role(client: TestClient, idempotency_key: str):
    """Test tenant creation without admin role fails."""
    tenant_data = {
        "name": "Test Barbershop",
        "slug": "test-barbershop"
    }
    
    headers = {"Idempotency-Key": idempotency_key}
    
    response = client.post("/tenants", json=tenant_data, headers=headers)
    
    assert response.status_code == 403


def test_create_tenant_invalid_slug(client: TestClient, admin_headers: dict, idempotency_key: str):
    """Test tenant creation with invalid slug fails."""
    tenant_data = {
        "name": "Test Barbershop",
        "slug": "admin"  # Reserved word
    }
    
    headers = {**admin_headers, "Idempotency-Key": idempotency_key}
    
    response = client.post("/tenants", json=tenant_data, headers=headers)
    
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "INVALID_SLUG"


def test_list_tenants(client: TestClient, admin_headers: dict):
    """Test listing tenants."""
    response = client.get("/tenants", headers=admin_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data


def test_list_tenants_without_admin_role(client: TestClient):
    """Test listing tenants without admin role fails."""
    response = client.get("/tenants")
    
    assert response.status_code == 403


def test_get_tenant_not_found(client: TestClient, admin_headers: dict):
    """Test getting non-existent tenant."""
    response = client.get("/tenants/non-existent", headers=admin_headers)
    
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "TENANT_NOT_FOUND"


def test_update_tenant_success(client: TestClient, admin_headers: dict, idempotency_key: str):
    """Test successful tenant update."""
    # First create a tenant
    tenant_data = {
        "name": "Original Name",
        "slug": "original-slug"
    }
    
    create_headers = {**admin_headers, "Idempotency-Key": idempotency_key}
    create_response = client.post("/tenants", json=tenant_data, headers=create_headers)
    tenant_id = create_response.json()["tenant_id"]
    
    # Update the tenant
    update_data = {
        "name": "Updated Name",
        "status": "disabled"
    }
    
    response = client.put(f"/tenants/{tenant_id}", json=update_data, headers=admin_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["status"] == "disabled"


def test_update_tenant_not_found(client: TestClient, admin_headers: dict):
    """Test updating non-existent tenant."""
    update_data = {
        "name": "Updated Name"
    }
    
    response = client.put("/tenants/non-existent", json=update_data, headers=admin_headers)
    
    assert response.status_code == 404
    data = response.json()
    assert data["error_code"] == "TENANT_NOT_FOUND"
