"""Tests for admin addons endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_create_addon(client: TestClient, admin_headers: dict):
    """Test creating an addon."""
    addon_data = {
        "code": "ai_booking",
        "name": "AI Booking",
        "meta_json": {"enabled": True}
    }
    
    response = client.post("/admin/addons/", json=addon_data, headers=admin_headers)
    assert response.status_code == 201
    
    data = response.json()
    assert data["code"] == "ai_booking"
    assert data["name"] == "AI Booking"
    assert data["meta_json"] == {"enabled": True}


def test_create_addon_duplicate(client: TestClient, admin_headers: dict):
    """Test creating a duplicate addon."""
    addon_data = {
        "code": "variable_pricing",
        "name": "Variable Pricing",
        "meta_json": {"enabled": True}
    }
    
    # Create first addon
    response = client.post("/admin/addons/", json=addon_data, headers=admin_headers)
    assert response.status_code == 201
    
    # Try to create duplicate
    response = client.post("/admin/addons/", json=addon_data, headers=admin_headers)
    assert response.status_code == 409


def test_list_addons(client: TestClient, admin_headers: dict):
    """Test listing addons."""
    # Create some addons
    addons = [
        {
            "code": "ai_booking",
            "name": "AI Booking",
            "meta_json": {"enabled": True}
        },
        {
            "code": "variable_pricing",
            "name": "Variable Pricing",
            "meta_json": {"enabled": True}
        }
    ]
    
    for addon in addons:
        client.post("/admin/addons/", json=addon, headers=admin_headers)
    
    response = client.get("/admin/addons/", headers=admin_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["addons"]) == 2
    assert data["total"] == 2


def test_get_addon(client: TestClient, admin_headers: dict):
    """Test getting an addon."""
    addon_data = {
        "code": "value_pack",
        "name": "Value Pack",
        "meta_json": {"packages": True, "upsell": True}
    }
    
    client.post("/admin/addons/", json=addon_data, headers=admin_headers)
    
    response = client.get("/admin/addons/value_pack", headers=admin_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["code"] == "value_pack"
    assert data["name"] == "Value Pack"


def test_get_addon_not_found(client: TestClient, admin_headers: dict):
    """Test getting a non-existent addon."""
    response = client.get("/admin/addons/nonexistent", headers=admin_headers)
    assert response.status_code == 404


def test_update_addon(client: TestClient, admin_headers: dict):
    """Test updating an addon."""
    addon_data = {
        "code": "family_booking",
        "name": "Family Booking",
        "meta_json": {"enabled": True}
    }
    
    client.post("/admin/addons/", json=addon_data, headers=admin_headers)
    
    update_data = {
        "name": "Updated Family Booking",
        "meta_json": {"enabled": True, "max_family_size": 5}
    }
    
    response = client.put("/admin/addons/family_booking", json=update_data, headers=admin_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Updated Family Booking"
    assert data["meta_json"] == {"enabled": True, "max_family_size": 5}


def test_delete_addon(client: TestClient, admin_headers: dict):
    """Test deleting an addon."""
    addon_data = {
        "code": "family_booking",
        "name": "Family Booking",
        "meta_json": {"enabled": True}
    }
    
    client.post("/admin/addons/", json=addon_data, headers=admin_headers)
    
    response = client.delete("/admin/addons/family_booking", headers=admin_headers)
    assert response.status_code == 204
    
    # Verify addon is deleted
    response = client.get("/admin/addons/family_booking", headers=admin_headers)
    assert response.status_code == 404


def test_admin_auth_required(client: TestClient):
    """Test that admin authentication is required."""
    addon_data = {
        "code": "ai_booking",
        "name": "AI Booking",
        "meta_json": {"enabled": True}
    }
    
    # Test without headers
    response = client.post("/admin/addons/", json=addon_data)
    assert response.status_code == 403
    
    # Test with wrong role
    response = client.post("/admin/addons/", json=addon_data, headers={"X-Internal-Role": "user"})
    assert response.status_code == 403
