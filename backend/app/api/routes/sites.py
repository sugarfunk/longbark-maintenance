from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from app.core.database import get_db
from app.models.user import User as UserModel
from app.models.site import Site as SiteModel, SiteStatus
from app.schemas.site import Site, SiteCreate, SiteUpdate
from app.api.routes.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[Site])
def list_sites(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[SiteStatus] = None,
    client_id: Optional[int] = None,
    search: Optional[str] = None,
) -> Any:
    """
    Retrieve sites with optional filters.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **status**: Filter by site status (active, paused, inactive)
    - **client_id**: Filter by client ID
    - **search**: Search by site name or URL
    """
    query = db.query(SiteModel)

    # Non-superusers can only see their own sites
    if not current_user.is_superuser:
        query = query.filter(SiteModel.owner_id == current_user.id)

    # Apply filters
    if status:
        query = query.filter(SiteModel.status == status)

    if client_id:
        query = query.filter(SiteModel.client_id == client_id)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                SiteModel.name.ilike(search_filter),
                SiteModel.url.ilike(search_filter),
            )
        )

    sites = query.offset(skip).limit(limit).all()
    return sites


@router.post("/", response_model=Site, status_code=status.HTTP_201_CREATED)
def create_site(
    *,
    db: Session = Depends(get_db),
    site_in: SiteCreate,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Create new site.
    """
    # Check if URL already exists
    existing_site = db.query(SiteModel).filter(SiteModel.url == site_in.url).first()
    if existing_site:
        raise HTTPException(
            status_code=400,
            detail="A site with this URL already exists.",
        )

    # Create site
    site = SiteModel(
        **site_in.model_dump(),
        owner_id=current_user.id,
    )
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.get("/{site_id}", response_model=Site)
def get_site(
    *,
    db: Session = Depends(get_db),
    site_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Get site by ID.
    """
    site = db.query(SiteModel).filter(SiteModel.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Check permissions
    if not current_user.is_superuser and site.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return site


@router.put("/{site_id}", response_model=Site)
def update_site(
    *,
    db: Session = Depends(get_db),
    site_id: int,
    site_in: SiteUpdate,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Update site.
    """
    site = db.query(SiteModel).filter(SiteModel.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Check permissions
    if not current_user.is_superuser and site.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Check if URL is being changed and if it already exists
    if site_in.url and site_in.url != site.url:
        existing_site = db.query(SiteModel).filter(SiteModel.url == site_in.url).first()
        if existing_site:
            raise HTTPException(
                status_code=400,
                detail="A site with this URL already exists.",
            )

    # Update site
    update_data = site_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(site, field, value)

    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_site(
    *,
    db: Session = Depends(get_db),
    site_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> None:
    """
    Delete site.
    """
    site = db.query(SiteModel).filter(SiteModel.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Check permissions
    if not current_user.is_superuser and site.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(site)
    db.commit()


@router.post("/{site_id}/check", status_code=status.HTTP_202_ACCEPTED)
def trigger_check(
    *,
    db: Session = Depends(get_db),
    site_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Trigger immediate check for a site.

    This endpoint queues a check task for the site. The actual check will be
    performed asynchronously by a background worker.
    """
    site = db.query(SiteModel).filter(SiteModel.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Check permissions
    if not current_user.is_superuser and site.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # TODO: Queue check task using Celery or background tasks
    # For now, just return a message
    return {
        "message": "Check queued successfully",
        "site_id": site_id,
        "site_name": site.name,
    }


@router.get("/{site_id}/status")
def get_site_status(
    *,
    db: Session = Depends(get_db),
    site_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Get current status of a site.

    Returns the most recent check results for quick status overview.
    """
    site = db.query(SiteModel).filter(SiteModel.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Check permissions
    if not current_user.is_superuser and site.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return {
        "site_id": site.id,
        "site_name": site.name,
        "url": site.url,
        "status": site.status,
        "last_checked_at": site.last_checked_at,
        "current_status_code": site.current_status_code,
        "current_response_time": site.current_response_time,
        "current_ssl_valid": site.current_ssl_valid,
        "current_ssl_expiry": site.current_ssl_expiry,
    }
