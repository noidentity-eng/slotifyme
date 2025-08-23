"""Admin plans router for CRUD operations."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db import get_db
from app.deps import require_admin
from app.services.plan_service import PlanService
from app.schemas.plan import PlanCreate, PlanUpdate, PlanResponse, PlanList

router = APIRouter(prefix="/admin/plans", tags=["admin"])


@router.post("/", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: PlanCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Create a new plan."""
    service = PlanService(db)
    try:
        plan = service.create_plan(plan_data)
        return plan
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Plan with this code already exists",
        )


@router.get("/", response_model=PlanList)
async def list_plans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """List all plans."""
    service = PlanService(db)
    plans = service.get_plans(skip=skip, limit=limit)
    return PlanList(plans=plans, total=len(plans))


@router.get("/{code}", response_model=PlanResponse)
async def get_plan(
    code: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Get a plan by code."""
    service = PlanService(db)
    plan = service.get_plan(code)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )
    return plan


@router.put("/{code}", response_model=PlanResponse)
async def update_plan(
    code: str,
    plan_data: PlanUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Update a plan."""
    service = PlanService(db)
    plan = service.update_plan(code, plan_data)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )
    return plan


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    code: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    """Delete a plan."""
    service = PlanService(db)
    try:
        success = service.delete_plan(code)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found",
            )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete plan that is in use by tenants",
        )
