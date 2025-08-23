"""Script to initialize database with seed data."""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from tenant.app.db import AsyncSessionLocal
from tenant.app.models.data_classification import DataClassificationRule, DataClassification
from tenant.app.logging import get_logger

logger = get_logger(__name__)


async def seed_data_classification():
    """Seed data classification rules."""
    async with AsyncSessionLocal() as session:
        # Check if data already exists
        existing = await session.execute(
            "SELECT COUNT(*) FROM data_classification"
        )
        if existing.scalar() > 0:
            logger.info("Data classification already seeded, skipping")
            return
        
        # Seed data classification rules
        rules = [
            # Tenants table
            ("tenants", "name", "public", False, "Tenant name"),
            ("tenants", "slug", "public", False, "Tenant slug"),
            ("tenants", "theme_json", "public", False, "Tenant theme/branding"),
            ("tenants", "status", "private", False, "Tenant status"),
            ("tenants", "created_at", "private", False, "Creation timestamp"),
            ("tenants", "updated_at", "private", False, "Update timestamp"),
            
            # Locations table
            ("locations", "slug", "public", False, "Location slug"),
            ("locations", "name", "public", False, "Location name"),
            ("locations", "timezone", "public", False, "IANA timezone"),
            ("locations", "status", "public", False, "Location status"),
            ("locations", "phone", "private", True, "Phone number (visibility controlled)"),
            ("locations", "phone_public", "public", False, "Phone visibility flag"),
            ("locations", "address_json", "private", False, "Location address"),
            ("locations", "created_at", "private", False, "Creation timestamp"),
            ("locations", "updated_at", "private", False, "Update timestamp"),
            
            # Tenant users table
            ("tenant_users", "tenant_id", "private", False, "Tenant ID"),
            ("tenant_users", "user_id", "private", False, "User ID"),
            ("tenant_users", "role", "private", False, "User role"),
            ("tenant_users", "created_at", "private", False, "Link creation timestamp"),
        ]
        
        for table_name, column_name, classification, visibility_controlled, description in rules:
            rule = DataClassificationRule(
                table_name=table_name,
                column_name=column_name,
                classification=DataClassification(classification),
                visibility_controlled=visibility_controlled,
                description=description
            )
            session.add(rule)
        
        await session.commit()
        logger.info(f"Seeded {len(rules)} data classification rules")


async def main():
    """Main function to initialize database."""
    logger.info("Starting database initialization")
    
    try:
        await seed_data_classification()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        raise


if __name__ == "__main__":
    asyncio.run(main())
