"""Tests for tenant assignment endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_update_tenant_plan(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test updating tenant plan."""
    # First create a plan
    plan_data = {
        "code": "silver",
        "name": "Silver Plan",
        "limits_json": {"locations": 1, "stylists": 5},
        "features_json": {"basic_reporting": True}
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    # Update tenant plan
    tenant_plan_data = {
        "plan_code": "silver",
        "meta": {"billing_cycle": "monthly"}
    }
    
    response = client.put("/tenants/ten_123/plan", json=tenant_plan_data, headers=internal_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["tenant_id"] == "ten_123"
    assert data["plan"]["code"] == "silver"
    assert data["plan"]["meta"] == {"billing_cycle": "monthly"}
    assert data["version"] == 1


def test_update_tenant_plan_invalid_plan(client: TestClient, internal_headers: dict):
    """Test updating tenant plan with invalid plan."""
    tenant_plan_data = {
        "plan_code": "nonexistent",
        "meta": {"billing_cycle": "monthly"}
    }
    
    response = client.put("/tenants/ten_123/plan", json=tenant_plan_data, headers=internal_headers)
    assert response.status_code == 404


def test_update_tenant_addons(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test updating tenant addons."""
    # First create a plan and addons
    plan_data = {
        "code": "silver",
        "name": "Silver Plan",
        "limits_json": {"locations": 1, "stylists": 5},
        "features_json": {"basic_reporting": True}
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    addon_data = {
        "code": "ai_booking",
        "name": "AI Booking",
        "meta_json": {"enabled": True}
    }
    client.post("/admin/addons/", json=addon_data, headers=admin_headers)
    
    # Assign plan to tenant first
    tenant_plan_data = {"plan_code": "silver"}
    client.put("/tenants/ten_123/plan", json=tenant_plan_data, headers=internal_headers)
    
    # Update tenant addons
    addon_update_data = {
        "add": ["ai_booking"],
        "remove": [],
        "upsert": []
    }
    
    response = client.put("/tenants/ten_123/addons", json=addon_update_data, headers=internal_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["tenant_id"] == "ten_123"
    assert len(data["addons"]) == 1
    assert data["addons"][0]["code"] == "ai_booking"
    assert data["version"] == 2  # Version bumped


def test_update_tenant_addons_invalid_addon(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test updating tenant addons with invalid addon."""
    # First create a plan
    plan_data = {
        "code": "silver",
        "name": "Silver Plan",
        "limits_json": {"locations": 1, "stylists": 5},
        "features_json": {"basic_reporting": True}
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    # Assign plan to tenant first
    tenant_plan_data = {"plan_code": "silver"}
    client.put("/tenants/ten_123/plan", json=tenant_plan_data, headers=internal_headers)
    
    # Try to add invalid addon
    addon_update_data = {
        "add": ["nonexistent_addon"],
        "remove": [],
        "upsert": []
    }
    
    response = client.put("/tenants/ten_123/addons", json=addon_update_data, headers=internal_headers)
    assert response.status_code == 404


def test_get_tenant_assignments(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test getting tenant assignments."""
    # First create a plan and addons
    plan_data = {
        "code": "gold",
        "name": "Gold Plan",
        "limits_json": {"locations": 2, "stylists": 10},
        "features_json": {"loyalty_points": True}
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    addon_data = {
        "code": "ai_booking",
        "name": "AI Booking",
        "meta_json": {"enabled": True}
    }
    client.post("/admin/addons/", json=addon_data, headers=admin_headers)
    
    # Assign plan to tenant
    tenant_plan_data = {"plan_code": "gold"}
    client.put("/tenants/ten_456/plan", json=tenant_plan_data, headers=internal_headers)
    
    # Add addon
    addon_update_data = {"add": ["ai_booking"]}
    client.put("/tenants/ten_456/addons", json=addon_update_data, headers=internal_headers)
    
    # Get assignments
    response = client.get("/tenants/ten_456/assignments", headers=internal_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["tenant_id"] == "ten_456"
    assert data["plan"]["code"] == "gold"
    assert len(data["addons"]) == 1
    assert data["addons"][0]["code"] == "ai_booking"


def test_get_tenant_assignments_not_found(client: TestClient, internal_headers: dict):
    """Test getting assignments for non-existent tenant."""
    response = client.get("/tenants/nonexistent/assignments", headers=internal_headers)
    assert response.status_code == 404


def test_internal_auth_required(client: TestClient, admin_headers: dict):
    """Test that internal service authentication is required."""
    # Test without headers
    response = client.put("/tenants/ten_123/plan", json={"plan_code": "silver"})
    assert response.status_code == 403
    
    # Test with admin headers (should work for plan assignment)
    plan_data = {
        "code": "silver",
        "name": "Silver Plan",
        "limits_json": {"locations": 1, "stylists": 5},
        "features_json": {"basic_reporting": True}
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    response = client.put("/tenants/ten_123/plan", json={"plan_code": "silver"}, headers=admin_headers)
    assert response.status_code == 403  # Admin headers don't work for tenant endpoints
