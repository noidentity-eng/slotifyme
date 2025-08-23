"""Versioning utilities for tenant plan changes."""

from sqlalchemy.orm import Session
from app.models.tenant_plan import TenantPlan


def bump_tenant_version(db: Session, tenant_id: str) -> int:
    """Bump tenant plan version and return new version."""
    tenant_plan = db.query(TenantPlan).filter(TenantPlan.tenant_id == tenant_id).first()
    
    if tenant_plan:
        tenant_plan.version += 1
        db.commit()
        return tenant_plan.version
    else:
        # Create new tenant plan with version 1
        tenant_plan = TenantPlan(
            tenant_id=tenant_id,
            plan_code="silver",  # Default plan
            version=1,
        )
        db.add(tenant_plan)
        db.commit()
        return 1
