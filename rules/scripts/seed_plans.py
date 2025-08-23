#!/usr/bin/env python3
"""Seed script for new plan structure."""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from app.db import get_db
from app.models.plan import Plan
from app.models.addon import Addon


def seed_plans(db: Session):
    """Seed the new plan structure."""
    
    # Delete existing plans and addons
    db.query(Plan).delete()
    db.query(Addon).delete()
    
    # Create Silver Plan
    silver_plan = Plan(
        code="silver",
        name="Silver",
        limits_json={
            "locations_included": 1,
            "stylists_included": 5
        },
        features_json={
            "basic_reporting": True
        },
        overage_policy_json={
            "allow_extra_locations": True,
            "allow_extra_stylists": True
        },
        pricing_ref="pricebook/plans/silver@v1"  # $99/month
    )
    
    # Create Gold Plan
    gold_plan = Plan(
        code="gold",
        name="Gold",
        limits_json={
            "locations_included": 2,
            "stylists_included": 10
        },
        features_json={
            "family_booking": True,
            "loyalty_points": True,
            "reviews": True,
            "advanced_analytics": True,
            "stylist_matching": True
        },
        overage_policy_json={
            "allow_extra_locations": True,
            "allow_extra_stylists": True
        },
        pricing_ref="pricebook/plans/gold@v1"  # $199/month
    )
    
    # Create Platinum Plan
    platinum_plan = Plan(
        code="platinum",
        name="Platinum",
        limits_json={
            "locations_included": 3,
            "stylists_included": 20
        },
        features_json={
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
        overage_policy_json={
            "allow_extra_locations": True,
            "allow_extra_stylists": True
        },
        pricing_ref="pricebook/plans/platinum@v1"  # $399/month
    )
    
    # Create Addons
    ai_booking_addon = Addon(
        code="ai_booking",
        name="AI Booking",
        meta_json={
            "description": "Enables AI-powered booking features"
        },
        effect_json={"ai_booking": True},
        pricing_ref="pricebook/addons/ai_booking@v1"  # $49.99/month
    )
    
    variable_pricing_addon = Addon(
        code="variable_pricing",
        name="Variable Pricing",
        meta_json={
            "description": "Enables dynamic pricing features"
        },
        effect_json={"variable_pricing": True},
        pricing_ref="pricebook/addons/variable_pricing@v1"  # $29.99/month
    )
    
    value_pack_addon = Addon(
        code="value_pack",
        name="Value Pack",
        meta_json={
            "description": "Package deals, upsell, and waitlist features"
        },
        effect_json={
            "packages": True,
            "upsell": True,
            "waitlist": True,
            "gift_cards": True
        },
        pricing_ref="pricebook/addons/value_pack@v2"  # $49.99/month
    )
    
    family_booking_addon = Addon(
        code="family_booking",
        name="Family Booking",
        meta_json={
            "description": "Family booking features for Silver plans"
        },
        effect_json={"family_booking": True},
        pricing_ref="pricebook/addons/family_booking@v1"  # $19.99/month
    )
    
    gift_cards_addon = Addon(
        code="gift_cards",
        name="Gift Cards",
        meta_json={
            "description": "Gift card features for Silver plans"
        },
        effect_json={"gift_cards": True},
        pricing_ref="pricebook/addons/gift_cards@v1"  # $9.99/month
    )
    
    # Add all to database
    db.add_all([
        silver_plan,
        gold_plan,
        platinum_plan,
        ai_booking_addon,
        variable_pricing_addon,
        value_pack_addon,
        family_booking_addon,
        gift_cards_addon
    ])
    
    db.commit()
    
    print("✅ Plans and addons seeded successfully!")
    print(f"   - Created 3 plans: Silver, Gold, Platinum")
    print(f"   - Created 5 addons: ai_booking, variable_pricing, value_pack, family_booking, gift_cards")


def main():
    """Main function to run the seed script."""
    print("🌱 Seeding plans and addons...")
    
    # Get database session
    db = next(get_db())
    
    try:
        seed_plans(db)
    except Exception as e:
        print(f"❌ Error seeding plans: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
