"""Addon service for managing addon features."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.addon import Addon
from app.models.tenant_addon import TenantAddon
from app.schemas.addon import AddonCreate, AddonUpdate


class AddonService:
    """Service for managing addons."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_addon(self, addon_data: AddonCreate) -> Addon:
        """Create a new addon."""
        addon = Addon(**addon_data.model_dump())
        self.db.add(addon)
        self.db.commit()
        self.db.refresh(addon)
        return addon
    
    def get_addon(self, code: str) -> Optional[Addon]:
        """Get addon by code."""
        return self.db.query(Addon).filter(Addon.code == code).first()
    
    def get_addons(self, skip: int = 0, limit: int = 100) -> List[Addon]:
        """Get list of addons."""
        return self.db.query(Addon).offset(skip).limit(limit).all()
    
    def update_addon(self, code: str, addon_data: AddonUpdate) -> Optional[Addon]:
        """Update an addon."""
        addon = self.get_addon(code)
        if not addon:
            return None
        
        for field, value in addon_data.model_dump().items():
            setattr(addon, field, value)
        
        self.db.commit()
        self.db.refresh(addon)
        return addon
    
    def delete_addon(self, code: str) -> bool:
        """Delete an addon."""
        addon = self.get_addon(code)
        if not addon:
            return False
        
        # Check if addon is in use
        tenant_addon = self.db.query(TenantAddon).filter(TenantAddon.addon_code == code).first()
        if tenant_addon:
            raise IntegrityError("Addon is in use by tenants", None, None)
        
        self.db.delete(addon)
        self.db.commit()
        return True
    
    def is_addon_in_use(self, code: str) -> bool:
        """Check if addon is in use by any tenant."""
        return self.db.query(TenantAddon).filter(TenantAddon.addon_code == code).first() is not None
