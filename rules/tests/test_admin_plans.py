"""Tests for admin plans endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.plan_service import PlanService


def test_create_plan(client: TestClient, admin_headers: dict):
    """Test creating a plan."""
    plan_data = {
        "code": "silver",
        "name": "Silver Plan",
        "limits_json": {"locations": 1, "stylists": 5},
        "features_json": {"basic_reporting": True}
    }
    
    response = client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    assert response.status_code == 201
    
    data = response.json()
    assert data["code"] == "silver"
    assert data["name"] == "Silver Plan"
    assert data["limits_json"] == {"locations": 1, "stylists": 5}
    assert data["features_json"] == {"basic_reporting": True}


def test_create_plan_duplicate(client: TestClient, admin_headers: dict):
    """Test creating a duplicate plan."""
    plan_data = {
        "code": "gold",
        "name": "Gold Plan",
        "limits_json": {"locations": 2, "stylists": 10},
        "features_json": {"loyalty_points": True}
    }
    
    # Create first plan
    response = client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    assert response.status_code == 201
    
    # Try to create duplicate
    response = client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    assert response.status_code == 409


def test_list_plans(client: TestClient, admin_headers: dict):
    """Test listing plans."""
    # Create some plans
    plans = [
        {
            "code": "silver",
            "name": "Silver Plan",
            "limits_json": {"locations": 1, "stylists": 5},
            "features_json": {"basic_reporting": True}
        },
        {
            "code": "gold",
            "name": "Gold Plan",
            "limits_json": {"locations": 2, "stylists": 10},
            "features_json": {"loyalty_points": True}
        }
    ]
    
    for plan in plans:
        client.post("/admin/plans/", json=plan, headers=admin_headers)
    
    response = client.get("/admin/plans/", headers=admin_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["plans"]) == 2
    assert data["total"] == 2


def test_get_plan(client: TestClient, admin_headers: dict):
    """Test getting a plan."""
    plan_data = {
        "code": "platinum",
        "name": "Platinum Plan",
        "limits_json": {"locations": 3, "stylists": 20},
        "features_json": {"online_store": True}
    }
    
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    response = client.get("/admin/plans/platinum", headers=admin_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["code"] == "platinum"
    assert data["name"] == "Platinum Plan"


def test_get_plan_not_found(client: TestClient, admin_headers: dict):
    """Test getting a non-existent plan."""
    response = client.get("/admin/plans/nonexistent", headers=admin_headers)
    assert response.status_code == 404


def test_update_plan(client: TestClient, admin_headers: dict):
    """Test updating a plan."""
    plan_data = {
        "code": "silver",
        "name": "Silver Plan",
        "limits_json": {"locations": 1, "stylists": 5},
        "features_json": {"basic_reporting": True}
    }
    
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    update_data = {
        "name": "Updated Silver Plan",
        "limits_json": {"locations": 2, "stylists": 8},
        "features_json": {"basic_reporting": True, "advanced_analytics": True}
    }
    
    response = client.put("/admin/plans/silver", json=update_data, headers=admin_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Updated Silver Plan"
    assert data["limits_json"] == {"locations": 2, "stylists": 8}


def test_delete_plan(client: TestClient, admin_headers: dict):
    """Test deleting a plan."""
    plan_data = {
        "code": "silver",
        "name": "Silver Plan",
        "limits_json": {"locations": 1, "stylists": 5},
        "features_json": {"basic_reporting": True}
    }
    
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    response = client.delete("/admin/plans/silver", headers=admin_headers)
    assert response.status_code == 204
    
    # Verify plan is deleted
    response = client.get("/admin/plans/silver", headers=admin_headers)
    assert response.status_code == 404


def test_admin_auth_required(client: TestClient):
    """Test that admin authentication is required."""
    plan_data = {
        "code": "silver",
        "name": "Silver Plan",
        "limits_json": {"locations": 1, "stylists": 5},
        "features_json": {"basic_reporting": True}
    }
    
    # Test without headers
    response = client.post("/admin/plans/", json=plan_data)
    assert response.status_code == 403
    
    # Test with wrong role
    response = client.post("/admin/plans/", json=plan_data, headers={"X-Internal-Role": "user"})
    assert response.status_code == 403
