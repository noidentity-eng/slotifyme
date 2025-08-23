"""Health check router."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from tenant.app.db import get_db
from tenant.app.deps import RequestID

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check(
    db: AsyncSession = Depends(get_db),
    request_id: str = RequestID
):
    """Health check endpoint."""
    # Check database connectivity
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    
    return {
        "status": "ok" if db_status == "ok" else "error",
        "database": db_status,
        "request_id": request_id
    }
