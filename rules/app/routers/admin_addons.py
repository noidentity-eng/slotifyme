"""Admin addons router for CRUD operations."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db import get_db
from app.deps import require_admin
from app.services.addon_service import AddonService
from app.schemas.addon import AddonCreate, AddonUpdate, AddonResponse, AddonList

router = APIRouter(prefix="/admin/addons", tags=["admin"])


@router.post("/", response_model=AddonResponse, status_code=status.HTTP_201_CREATED)
async def create_addon(
    addon_data: AddonCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Create a new addon."""
    service = AddonService(db)
    try:
        addon = service.create_addon(addon_data)
        return addon
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Addon with this code already exists",
        )


@router.get("/", response_model=AddonList)
async def list_addons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """List all addons."""
    service = AddonService(db)
    addons = service.get_addons(skip=skip, limit=limit)
    return AddonList(addons=addons, total=len(addons))


@router.get("/{code}", response_model=AddonResponse)
async def get_addon(
    code: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Get an addon by code."""
    service = AddonService(db)
    addon = service.get_addon(code)
    if not addon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Addon not found",
        )
    return addon


@router.put("/{code}", response_model=AddonResponse)
async def update_addon(
    code: str,
    addon_data: AddonUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Update an addon."""
    service = AddonService(db)
    addon = service.update_addon(code, addon_data)
    if not addon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Addon not found",
        )
    return addon


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_addon(
    code: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Delete an addon."""
    service = AddonService(db)
    try:
        success = service.delete_addon(code)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Addon not found",
            )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete addon that is in use by tenants",
        )
