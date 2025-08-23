"""Plan service for managing subscription plans."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.plan import Plan
from app.models.tenant_plan import TenantPlan
from app.schemas.plan import PlanCreate, PlanUpdate


class PlanService:
    """Service for managing plans."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_plan(self, plan_data: PlanCreate) -> Plan:
        """Create a new plan."""
        plan = Plan(**plan_data.model_dump())
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan
    
    def get_plan(self, code: str) -> Optional[Plan]:
        """Get plan by code."""
        return self.db.query(Plan).filter(Plan.code == code).first()
    
    def get_plans(self, skip: int = 0, limit: int = 100) -> List[Plan]:
        """Get list of plans."""
        return self.db.query(Plan).offset(skip).limit(limit).all()
    
    def update_plan(self, code: str, plan_data: PlanUpdate) -> Optional[Plan]:
        """Update a plan."""
        plan = self.get_plan(code)
        if not plan:
            return None
        
        for field, value in plan_data.model_dump().items():
            setattr(plan, field, value)
        
        self.db.commit()
        self.db.refresh(plan)
        return plan
    
    def delete_plan(self, code: str) -> bool:
        """Delete a plan."""
        plan = self.get_plan(code)
        if not plan:
            return False
        
        # Check if plan is in use
        tenant_plan = self.db.query(TenantPlan).filter(TenantPlan.plan_code == code).first()
        if tenant_plan:
            raise IntegrityError("Plan is in use by tenants", None, None)
        
        self.db.delete(plan)
        self.db.commit()
        return True
    
    def is_plan_in_use(self, code: str) -> bool:
        """Check if plan is in use by any tenant."""
        return self.db.query(TenantPlan).filter(TenantPlan.plan_code == code).first() is not None
