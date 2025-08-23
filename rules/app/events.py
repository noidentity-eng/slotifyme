"""Event handling for plan and addon changes."""

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class PlanChangedEvent:
    """Event emitted when a tenant's plan changes."""
    
    def __init__(self, tenant_id: str, old_plan: str = None, new_plan: str = None):
        self.tenant_id = tenant_id
        self.old_plan = old_plan
        self.new_plan = new_plan
        self.timestamp = datetime.utcnow()


class AddOnChangedEvent:
    """Event emitted when a tenant's addons change."""
    
    def __init__(self, tenant_id: str, changes: dict[str, Any]):
        self.tenant_id = tenant_id
        self.changes = changes
        self.timestamp = datetime.utcnow()


async def emit_plan_changed(tenant_id: str, old_plan: str = None, new_plan: str = None):
    """Emit plan changed event."""
    event = PlanChangedEvent(tenant_id, old_plan, new_plan)
    logger.info(
        "Plan changed event: tenant_id=%s, old_plan=%s, new_plan=%s",
        event.tenant_id,
        event.old_plan,
        event.new_plan,
    )
    # TODO: Send to message bus in production
    return event


async def emit_addon_changed(tenant_id: str, changes: dict[str, Any]):
    """Emit addon changed event."""
    event = AddOnChangedEvent(tenant_id, changes)
    logger.info(
        "Addon changed event: tenant_id=%s, changes=%s",
        event.tenant_id,
        event.changes,
    )
    # TODO: Send to message bus in production
    return event
