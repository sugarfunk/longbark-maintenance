from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from app.core.database import get_db
from app.models.user import User as UserModel
from app.models.site import Site as SiteModel
from app.models.alert import (
    Alert as AlertModel,
    AlertType,
    AlertSeverity,
    AlertStatus,
)
from app.schemas.alert import Alert, AlertUpdate, AlertAcknowledge, AlertResolve
from app.api.routes.auth import get_current_active_user

router = APIRouter()


def verify_alert_access(
    alert_id: int, db: Session, current_user: UserModel
) -> AlertModel:
    """
    Helper function to verify user has access to an alert.
    """
    alert = db.query(AlertModel).filter(AlertModel.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Check permissions - user must own the site
    site = db.query(SiteModel).filter(SiteModel.id == alert.site_id).first()
    if not current_user.is_superuser and site.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return alert


@router.get("/", response_model=List[Alert])
def list_alerts(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[AlertStatus] = None,
    severity: Optional[AlertSeverity] = None,
    alert_type: Optional[AlertType] = None,
    site_id: Optional[int] = None,
) -> Any:
    """
    Retrieve alerts with optional filters.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **status**: Filter by alert status (open, acknowledged, resolved)
    - **severity**: Filter by severity (info, warning, error, critical)
    - **alert_type**: Filter by alert type
    - **site_id**: Filter by site ID
    """
    query = db.query(AlertModel)

    # Non-superusers can only see alerts for their own sites
    if not current_user.is_superuser:
        # Get all site IDs owned by the user
        user_site_ids = (
            db.query(SiteModel.id)
            .filter(SiteModel.owner_id == current_user.id)
            .all()
        )
        user_site_ids = [site_id[0] for site_id in user_site_ids]
        query = query.filter(AlertModel.site_id.in_(user_site_ids))

    # Apply filters
    if status:
        query = query.filter(AlertModel.status == status)

    if severity:
        query = query.filter(AlertModel.severity == severity)

    if alert_type:
        query = query.filter(AlertModel.alert_type == alert_type)

    if site_id:
        query = query.filter(AlertModel.site_id == site_id)

    # Order by most recent first
    query = query.order_by(AlertModel.created_at.desc())

    alerts = query.offset(skip).limit(limit).all()
    return alerts


@router.get("/{alert_id}", response_model=Alert)
def get_alert(
    *,
    db: Session = Depends(get_db),
    alert_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Get alert by ID.
    """
    alert = verify_alert_access(alert_id, db, current_user)
    return alert


@router.put("/{alert_id}/acknowledge", response_model=Alert)
def acknowledge_alert(
    *,
    db: Session = Depends(get_db),
    alert_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    data: AlertAcknowledge,
) -> Any:
    """
    Acknowledge an alert.

    This marks the alert as acknowledged, indicating that someone is aware of
    the issue and working on it.
    """
    alert = verify_alert_access(alert_id, db, current_user)

    # Check if alert is already resolved
    if alert.status == AlertStatus.RESOLVED:
        raise HTTPException(
            status_code=400,
            detail="Cannot acknowledge a resolved alert",
        )

    # Update alert status
    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_at = datetime.utcnow()

    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.put("/{alert_id}/resolve", response_model=Alert)
def resolve_alert(
    *,
    db: Session = Depends(get_db),
    alert_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    data: AlertResolve,
) -> Any:
    """
    Resolve an alert.

    This marks the alert as resolved, indicating that the issue has been fixed.
    """
    alert = verify_alert_access(alert_id, db, current_user)

    # Check if alert is already resolved
    if alert.status == AlertStatus.RESOLVED:
        raise HTTPException(
            status_code=400,
            detail="Alert is already resolved",
        )

    # Update alert status
    alert.status = AlertStatus.RESOLVED
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = current_user.id
    if data.resolution_notes:
        alert.resolution_notes = data.resolution_notes

    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    *,
    db: Session = Depends(get_db),
    alert_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> None:
    """
    Delete alert.

    Note: This permanently deletes the alert. Consider resolving alerts instead
    of deleting them to maintain historical records.
    """
    alert = verify_alert_access(alert_id, db, current_user)

    db.delete(alert)
    db.commit()
