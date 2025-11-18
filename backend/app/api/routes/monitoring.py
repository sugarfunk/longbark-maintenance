from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user import User as UserModel
from app.models.site import Site as SiteModel
from app.models.monitoring import (
    UptimeCheck as UptimeCheckModel,
    SSLCheck as SSLCheckModel,
    PerformanceCheck as PerformanceCheckModel,
    BrokenLinkCheck as BrokenLinkCheckModel,
)
from app.schemas.monitoring import (
    UptimeCheck,
    SSLCheck,
    PerformanceCheck,
    BrokenLinkCheck,
)
from app.api.routes.auth import get_current_active_user

router = APIRouter()


def verify_site_access(
    site_id: int, db: Session, current_user: UserModel
) -> SiteModel:
    """
    Helper function to verify user has access to a site.
    """
    site = db.query(SiteModel).filter(SiteModel.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Check permissions
    if not current_user.is_superuser and site.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return site


@router.get("/uptime/{site_id}", response_model=List[UptimeCheck])
def get_uptime_history(
    *,
    db: Session = Depends(get_db),
    site_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Any:
    """
    Get uptime check history for a site.

    - **site_id**: Site ID to get history for
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **start_date**: Filter results from this date (ISO format)
    - **end_date**: Filter results until this date (ISO format)
    """
    # Verify access
    verify_site_access(site_id, db, current_user)

    # Build query
    query = db.query(UptimeCheckModel).filter(UptimeCheckModel.site_id == site_id)

    # Apply date filters
    if start_date:
        query = query.filter(UptimeCheckModel.checked_at >= start_date)
    if end_date:
        query = query.filter(UptimeCheckModel.checked_at <= end_date)

    # Order by most recent first
    query = query.order_by(UptimeCheckModel.checked_at.desc())

    checks = query.offset(skip).limit(limit).all()
    return checks


@router.get("/ssl/{site_id}", response_model=List[SSLCheck])
def get_ssl_history(
    *,
    db: Session = Depends(get_db),
    site_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Any:
    """
    Get SSL check history for a site.

    - **site_id**: Site ID to get history for
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **start_date**: Filter results from this date (ISO format)
    - **end_date**: Filter results until this date (ISO format)
    """
    # Verify access
    verify_site_access(site_id, db, current_user)

    # Build query
    query = db.query(SSLCheckModel).filter(SSLCheckModel.site_id == site_id)

    # Apply date filters
    if start_date:
        query = query.filter(SSLCheckModel.checked_at >= start_date)
    if end_date:
        query = query.filter(SSLCheckModel.checked_at <= end_date)

    # Order by most recent first
    query = query.order_by(SSLCheckModel.checked_at.desc())

    checks = query.offset(skip).limit(limit).all()
    return checks


@router.get("/performance/{site_id}", response_model=List[PerformanceCheck])
def get_performance_history(
    *,
    db: Session = Depends(get_db),
    site_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Any:
    """
    Get performance check history for a site.

    - **site_id**: Site ID to get history for
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **start_date**: Filter results from this date (ISO format)
    - **end_date**: Filter results until this date (ISO format)
    """
    # Verify access
    verify_site_access(site_id, db, current_user)

    # Build query
    query = db.query(PerformanceCheckModel).filter(
        PerformanceCheckModel.site_id == site_id
    )

    # Apply date filters
    if start_date:
        query = query.filter(PerformanceCheckModel.checked_at >= start_date)
    if end_date:
        query = query.filter(PerformanceCheckModel.checked_at <= end_date)

    # Order by most recent first
    query = query.order_by(PerformanceCheckModel.checked_at.desc())

    checks = query.offset(skip).limit(limit).all()
    return checks


@router.get("/broken-links/{site_id}", response_model=List[BrokenLinkCheck])
def get_broken_links_history(
    *,
    db: Session = Depends(get_db),
    site_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Any:
    """
    Get broken link check history for a site.

    - **site_id**: Site ID to get history for
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **start_date**: Filter results from this date (ISO format)
    - **end_date**: Filter results until this date (ISO format)
    """
    # Verify access
    verify_site_access(site_id, db, current_user)

    # Build query
    query = db.query(BrokenLinkCheckModel).filter(
        BrokenLinkCheckModel.site_id == site_id
    )

    # Apply date filters
    if start_date:
        query = query.filter(BrokenLinkCheckModel.checked_at >= start_date)
    if end_date:
        query = query.filter(BrokenLinkCheckModel.checked_at <= end_date)

    # Order by most recent first
    query = query.order_by(BrokenLinkCheckModel.checked_at.desc())

    checks = query.offset(skip).limit(limit).all()
    return checks
