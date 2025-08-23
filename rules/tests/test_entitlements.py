"""Tests for entitlements computation and caching."""

import pytest
from fastapi.testclient import TestClient


def test_compute_entitlements_silver_plan(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test computing entitlements for Silver plan."""
    # Create Silver plan
    plan_data = {
        "code": "silver",
        "name": "Silver Plan",
        "limits_json": {"locations": 1, "stylists": 5},
        "features_json": {"basic_reporting": True}
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    # Assign plan to tenant
    tenant_plan_data = {"plan_code": "silver"}
    client.put("/tenants/ten_123/plan", json=tenant_plan_data, headers=internal_headers)
    
    # Get entitlements
    response = client.get("/entitlements/ten_123", headers=internal_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["tenant_id"] == "ten_123"
    assert data["plan"] == "silver"
    assert data["limits"] == {"locations": 1, "stylists": 5}
    assert data["features"]["basic_reporting"] is True
    assert data["version"] == 1


def test_compute_entitlements_with_addons(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test computing entitlements with addons."""
    # Create Gold plan
    plan_data = {
        "code": "gold",
        "name": "Gold Plan",
        "limits_json": {"locations": 2, "stylists": 10},
        "features_json": {
            "loyalty_points": True,
            "reviews": True,
            "advanced_analytics": True
        }
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    # Create addons
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
    
    # Assign plan to tenant
    tenant_plan_data = {"plan_code": "gold"}
    client.put("/tenants/ten_456/plan", json=tenant_plan_data, headers=internal_headers)
    
    # Add addons
    addon_update_data = {"add": ["ai_booking", "variable_pricing"]}
    client.put("/tenants/ten_456/addons", json=addon_update_data, headers=internal_headers)
    
    # Get entitlements
    response = client.get("/entitlements/ten_456", headers=internal_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["tenant_id"] == "ten_456"
    assert data["plan"] == "gold"
    assert data["limits"] == {"locations": 2, "stylists": 10}
    assert data["features"]["loyalty_points"] is True
    assert data["features"]["ai_booking"] is True
    assert data["features"]["variable_pricing"] is True
    assert data["addons"]["ai_booking"] is True
    assert data["addons"]["variable_pricing"] is True


def test_compute_entitlements_value_pack_gold(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test computing entitlements with value_pack on Gold plan."""
    # Create Gold plan
    plan_data = {
        "code": "gold",
        "name": "Gold Plan",
        "limits_json": {"locations": 2, "stylists": 10},
        "features_json": {"loyalty_points": True}
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    # Create value_pack addon
    addon_data = {
        "code": "value_pack",
        "name": "Value Pack",
        "meta_json": {"packages": True, "upsell": True}
    }
    client.post("/admin/addons/", json=addon_data, headers=admin_headers)
    
    # Assign plan to tenant
    tenant_plan_data = {"plan_code": "gold"}
    client.put("/tenants/ten_789/plan", json=tenant_plan_data, headers=internal_headers)
    
    # Add value_pack
    addon_update_data = {"add": ["value_pack"]}
    client.put("/tenants/ten_789/addons", json=addon_update_data, headers=internal_headers)
    
    # Get entitlements
    response = client.get("/entitlements/ten_789", headers=internal_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["tenant_id"] == "ten_789"
    assert data["plan"] == "gold"
    assert data["addons"]["value_pack"]["packages"] is True
    assert data["addons"]["value_pack"]["upsell"] is True
    assert data["addons"]["value_pack"]["waitlist"] is True
    assert data["addons"]["value_pack"]["gift_cards"] is True  # Gold plan includes gift_cards


def test_compute_entitlements_family_booking_silver(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test computing entitlements with family_booking on Silver plan."""
    # Create Silver plan
    plan_data = {
        "code": "silver",
        "name": "Silver Plan",
        "limits_json": {"locations": 1, "stylists": 5},
        "features_json": {"basic_reporting": True}
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    # Create family_booking addon
    addon_data = {
        "code": "family_booking",
        "name": "Family Booking",
        "meta_json": {"enabled": True}
    }
    client.post("/admin/addons/", json=addon_data, headers=admin_headers)
    
    # Assign plan to tenant
    tenant_plan_data = {"plan_code": "silver"}
    client.put("/tenants/ten_101/plan", json=tenant_plan_data, headers=internal_headers)
    
    # Add family_booking
    addon_update_data = {"add": ["family_booking"]}
    client.put("/tenants/ten_101/addons", json=addon_update_data, headers=internal_headers)
    
    # Get entitlements
    response = client.get("/entitlements/ten_101", headers=internal_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["tenant_id"] == "ten_101"
    assert data["plan"] == "silver"
    assert data["features"]["family_booking"] is True  # Should be enabled for Silver
    assert data["addons"]["family_booking"] is True


def test_compute_entitlements_tenant_not_found(client: TestClient, internal_headers: dict):
    """Test computing entitlements for non-existent tenant."""
    response = client.get("/entitlements/nonexistent", headers=internal_headers)
    assert response.status_code == 404


def test_entitlements_etag_header(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test that entitlements response includes ETag header."""
    # Create plan and assign to tenant
    plan_data = {
        "code": "silver",
        "name": "Silver Plan",
        "limits_json": {"locations": 1, "stylists": 5},
        "features_json": {"basic_reporting": True}
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    tenant_plan_data = {"plan_code": "silver"}
    client.put("/tenants/ten_123/plan", json=tenant_plan_data, headers=internal_headers)
    
    # Get entitlements
    response = client.get("/entitlements/ten_123", headers=internal_headers)
    assert response.status_code == 200
    assert "ETag" in response.headers


def test_internal_auth_required_entitlements(client: TestClient):
    """Test that internal service authentication is required for entitlements."""
    response = client.get("/entitlements/ten_123")
    assert response.status_code == 403
