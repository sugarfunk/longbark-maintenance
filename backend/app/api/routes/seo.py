"""SEO monitoring routes"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.models import Site, SEOCheck, KeywordRanking
from app.api.routes.auth import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/{site_id}")
async def get_seo_checks(
    site_id: int,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get SEO check history for a site"""
    # Verify site exists and user has permission
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    if not current_user.is_superuser and site.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Build query
    query = db.query(SEOCheck).filter(SEOCheck.site_id == site_id)
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(SEOCheck.checked_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(SEOCheck.checked_at <= datetime.fromisoformat(end_date))
    
    # Get results
    checks = query.order_by(SEOCheck.checked_at.desc()).offset(skip).limit(limit).all()
    
    return checks


@router.get("/{site_id}/keywords")
async def get_keyword_rankings(
    site_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get keyword rankings for a site"""
    # Verify site exists and user has permission
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    if not current_user.is_superuser and site.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    rankings = db.query(KeywordRanking).filter(
        KeywordRanking.site_id == site_id
    ).order_by(KeywordRanking.checked_at.desc()).offset(skip).limit(limit).all()
    
    return rankings
