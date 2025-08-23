"""Tests for new entitlements functionality."""

import pytest
from fastapi.testclient import TestClient

from tests.conftest import client, admin_headers, internal_headers


def test_create_silver_plan_with_new_fields(client: TestClient, admin_headers: dict):
    """Test creating a Silver plan with new domain fields."""
    plan_data = {
        "code": "silver",
        "name": "Silver",
        "limits_json": {
            "locations_included": 1,
            "stylists_included": 5
        },
        "features_json": {
            "basic_reporting": True
        },
        "overage_policy_json": {
            "allow_extra_locations": True,
            "allow_extra_stylists": True
        },
        "pricing_ref": "pricebook/plans/silver@v1"
    }
    
    response = client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    assert response.status_code == 201
    
    data = response.json()
    assert data["code"] == "silver"
    assert data["limits_json"]["locations_included"] == 1
    assert data["features_json"]["basic_reporting"] is True
    assert data["overage_policy_json"]["allow_extra_locations"] is True
    assert data["pricing_ref"] == "pricebook/plans/silver@v1"


def test_create_gold_plan_with_advanced_features(client: TestClient, admin_headers: dict):
    """Test creating a Gold plan with advanced features."""
    plan_data = {
        "code": "gold",
        "name": "Gold",
        "limits_json": {
            "locations_included": 2,
            "stylists_included": 10
        },
        "features_json": {
            "family_booking": True,
            "loyalty_points": True,
            "reviews": True,
            "advanced_analytics": True,
            "stylist_matching": True
        },
        "overage_policy_json": {
            "allow_extra_locations": True,
            "allow_extra_stylists": True
        },
        "pricing_ref": "pricebook/plans/gold@v1"
    }
    
    response = client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    assert response.status_code == 201
    
    data = response.json()
    assert data["code"] == "gold"
    assert data["features_json"]["advanced_analytics"] is True
    assert data["features_json"]["stylist_matching"] is True


def test_assign_silver_plan_with_pricing_ref(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test assigning a Silver plan with pricing reference."""
    # Create plan first
    plan_data = {
        "code": "silver",
        "name": "Silver",
        "limits_json": {"locations_included": 1, "stylists_included": 5},
        "features_json": {"basic_reporting": True},
        "overage_policy_json": {"allow_extra_locations": True, "allow_extra_stylists": True}
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    # Assign plan with pricing ref
    assignment_data = {
        "plan_code": "silver",
        "pricing_ref": "pricebook/plans/silver@v2",
        "meta": {"source": "test"}
    }
    
    response = client.put("/tenants/ten_123/plan", json=assignment_data, headers=internal_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["plan"]["code"] == "silver"
    assert data["version"] == 1


def test_compute_entitlements_silver_baseline(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test computing entitlements for Silver plan baseline."""
    # Create Silver plan
    plan_data = {
        "code": "silver",
        "name": "Silver",
        "limits_json": {"locations_included": 1, "stylists_included": 5},
        "features_json": {"basic_reporting": True},
        "overage_policy_json": {"allow_extra_locations": True, "allow_extra_stylists": True},
        "pricing_ref": "pricebook/plans/silver@v1"
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    # Assign plan
    assignment_data = {"plan_code": "silver"}
    client.put("/tenants/ten_123/plan", json=assignment_data, headers=internal_headers)
    
    # Get entitlements
    response = client.get("/entitlements/ten_123", headers=internal_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["tenant_id"] == "ten_123"
    assert data["plan"] == "silver"
    assert data["limits"]["locations"] == 1
    assert data["limits"]["stylists"] == 5
    assert data["features"]["basic_reporting"] is True
    assert data["overage_policy"]["allow_extra_locations"] is True
    assert data["pricing_refs"]["plan"] == "pricebook/plans/silver@v1"


def test_compute_entitlements_with_addons(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test computing entitlements with addons."""
    # Create Silver plan
    plan_data = {
        "code": "silver",
        "name": "Silver",
        "limits_json": {"locations_included": 1, "stylists_included": 5},
        "features_json": {"basic_reporting": True},
        "overage_policy_json": {"allow_extra_locations": True, "allow_extra_stylists": True}
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    # Create addons
    ai_booking_addon = {
        "code": "ai_booking",
        "name": "AI Booking",
        "meta_json": {"description": "AI booking features"},
        "effect_json": {"ai_booking": True},
        "pricing_ref": "pricebook/addons/ai_booking@v1"
    }
    client.post("/admin/addons/", json=ai_booking_addon, headers=admin_headers)
    
    variable_pricing_addon = {
        "code": "variable_pricing",
        "name": "Variable Pricing",
        "meta_json": {"description": "Variable pricing features"},
        "effect_json": {"variable_pricing": True},
        "pricing_ref": "pricebook/addons/variable_pricing@v1"
    }
    client.post("/admin/addons/", json=variable_pricing_addon, headers=admin_headers)
    
    # Assign plan
    assignment_data = {"plan_code": "silver"}
    client.put("/tenants/ten_456/plan", json=assignment_data, headers=internal_headers)
    
    # Add addons
    addon_data = {
        "add": ["ai_booking", "variable_pricing"]
    }
    client.put("/tenants/ten_456/addons", json=addon_data, headers=internal_headers)
    
    # Get entitlements
    response = client.get("/entitlements/ten_456", headers=internal_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["features"]["ai_booking"] is True
    assert data["features"]["variable_pricing"] is True
    assert data["features"]["basic_reporting"] is True


def test_value_pack_addon_behavior(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test value pack addon behavior across plans."""
    # Create plans
    silver_plan = {
        "code": "silver",
        "name": "Silver",
        "limits_json": {"locations_included": 1, "stylists_included": 5},
        "features_json": {"basic_reporting": True},
        "overage_policy_json": {"allow_extra_locations": True, "allow_extra_stylists": True}
    }
    client.post("/admin/plans/", json=silver_plan, headers=admin_headers)
    
    gold_plan = {
        "code": "gold",
        "name": "Gold",
        "limits_json": {"locations_included": 2, "stylists_included": 10},
        "features_json": {"family_booking": True, "advanced_analytics": True},
        "overage_policy_json": {"allow_extra_locations": True, "allow_extra_stylists": True}
    }
    client.post("/admin/plans/", json=gold_plan, headers=admin_headers)
    
    # Create value pack addon
    value_pack_addon = {
        "code": "value_pack",
        "name": "Value Pack",
        "meta_json": {"description": "Value pack features"},
        "effect_json": {"packages": True, "upsell": True, "waitlist": True, "gift_cards": True},
        "pricing_ref": "pricebook/addons/value_pack@v2"
    }
    client.post("/admin/addons/", json=value_pack_addon, headers=admin_headers)
    
    # Test Silver + value_pack
    client.put("/tenants/ten_silver/plan", json={"plan_code": "silver"}, headers=internal_headers)
    client.put("/tenants/ten_silver/addons", json={"add": ["value_pack"]}, headers=internal_headers)
    
    response = client.get("/entitlements/ten_silver", headers=internal_headers)
    data = response.json()
    assert data["features"]["packages"] is True
    assert data["features"]["upsell"] is True
    assert data["features"]["waitlist"] is True
    assert data["features"]["gift_cards"] is True  # Value pack includes gift_cards
    
    # Test Gold + value_pack
    client.put("/tenants/ten_gold/plan", json={"plan_code": "gold"}, headers=internal_headers)
    client.put("/tenants/ten_gold/addons", json={"add": ["value_pack"]}, headers=internal_headers)
    
    response = client.get("/entitlements/ten_gold", headers=internal_headers)
    data = response.json()
    assert data["features"]["packages"] is True
    assert data["features"]["upsell"] is True
    assert data["features"]["waitlist"] is True
    assert data["features"]["gift_cards"] is True  # Gold gets gift_cards


def test_tenant_overrides(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test tenant limit overrides."""
    # Create Silver plan
    plan_data = {
        "code": "silver",
        "name": "Silver",
        "limits_json": {"locations_included": 1, "stylists_included": 5},
        "features_json": {"basic_reporting": True},
        "overage_policy_json": {"allow_extra_locations": True, "allow_extra_stylists": True}
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    # Assign plan
    client.put("/tenants/ten_789/plan", json={"plan_code": "silver"}, headers=internal_headers)
    
    # Add overrides
    override_data = {
        "upsert": [
            {"key": "locations_included", "value": 3},
            {"key": "discount_tier", "value": 0.1}
        ]
    }
    response = client.put("/tenants/ten_789/overrides", json=override_data, headers=internal_headers)
    assert response.status_code == 200
    
    # Get entitlements
    response = client.get("/entitlements/ten_789", headers=internal_headers)
    data = response.json()
    assert data["limits"]["locations"] == 3  # Overridden
    # Note: billing field was removed in favor of pricing_refs


def test_remove_overrides(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test removing tenant overrides."""
    # Create Silver plan
    plan_data = {
        "code": "silver",
        "name": "Silver",
        "limits_json": {"locations_included": 1, "stylists_included": 5},
        "features_json": {"basic_reporting": True},
        "overage_policy_json": {"allow_extra_locations": True, "allow_extra_stylists": True}
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    # Assign plan
    client.put("/tenants/ten_override/plan", json={"plan_code": "silver"}, headers=internal_headers)
    
    # Add override
    override_data = {
        "upsert": [{"key": "locations_included", "value": 5}]
    }
    client.put("/tenants/ten_override/overrides", json=override_data, headers=internal_headers)
    
    # Verify override is applied
    response = client.get("/entitlements/ten_override", headers=internal_headers)
    data = response.json()
    assert data["limits"]["locations"] == 5
    
    # Remove override
    remove_data = {
        "remove": ["locations_included"]
    }
    client.put("/tenants/ten_override/overrides", json=remove_data, headers=internal_headers)
    
    # Verify override is removed
    response = client.get("/entitlements/ten_override", headers=internal_headers)
    data = response.json()
    assert data["limits"]["locations"] == 1  # Back to plan default


def test_etag_changes_with_updates(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test that ETag changes when entitlements change."""
    # Create Silver plan
    plan_data = {
        "code": "silver",
        "name": "Silver",
        "limits_json": {"locations_included": 1, "stylists_included": 5},
        "features_json": {"basic_reporting": True},
        "overage_policy_json": {"allow_extra_locations": True, "allow_extra_stylists": True}
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    # Assign plan
    client.put("/tenants/ten_etag/plan", json={"plan_code": "silver"}, headers=internal_headers)
    
    # Get initial entitlements
    response1 = client.get("/entitlements/ten_etag", headers=internal_headers)
    etag1 = response1.headers.get("ETag")
    assert etag1 is not None
    
    # Add addon
    client.post("/admin/addons/", json={
        "code": "ai_booking",
        "name": "AI Booking",
        "meta_json": {"description": "AI booking features"},
        "effect_json": {"ai_booking": True},
        "pricing_ref": "pricebook/addons/ai_booking@v1"
    }, headers=admin_headers)
    
    client.put("/tenants/ten_etag/addons", json={"add": ["ai_booking"]}, headers=internal_headers)
    
    # Get updated entitlements
    response2 = client.get("/entitlements/ten_etag", headers=internal_headers)
    etag2 = response2.headers.get("ETag")
    assert etag2 is not None
    assert etag1 != etag2  # ETag should change


def test_platinum_plan_features(client: TestClient, admin_headers: dict, internal_headers: dict):
    """Test Platinum plan includes advanced features by default."""
    # Create Platinum plan
    plan_data = {
        "code": "platinum",
        "name": "Platinum",
        "limits_json": {"locations_included": 3, "stylists_included": 20},
        "features_json": {
            "online_store": True,
            "tiered_loyalty": True,
            "memberships": True,
            "smart_no_shows": True,
            "dynamic_pricing": True,
            "ai_promotions": True,
            "staff_utilization": True,
            "offline_mode": True,
            "data_export": True,
            "voice_assistant": True
        },
        "overage_policy_json": {"allow_extra_locations": True, "allow_extra_stylists": True},
        "pricing_ref": "pricebook/plans/platinum@v1"
    }
    client.post("/admin/plans/", json=plan_data, headers=admin_headers)
    
    # Assign plan
    client.put("/tenants/ten_platinum/plan", json={"plan_code": "platinum"}, headers=internal_headers)
    
    # Get entitlements
    response = client.get("/entitlements/ten_platinum", headers=internal_headers)
    data = response.json()
    
    # Verify all Platinum features are present
    assert data["features"]["online_store"] is True
    assert data["features"]["tiered_loyalty"] is True
    assert data["features"]["memberships"] is True
    assert data["features"]["smart_no_shows"] is True
    assert data["features"]["dynamic_pricing"] is True
    assert data["features"]["ai_promotions"] is True
    assert data["features"]["staff_utilization"] is True
    assert data["features"]["offline_mode"] is True
    assert data["features"]["data_export"] is True
    assert data["features"]["voice_assistant"] is True
