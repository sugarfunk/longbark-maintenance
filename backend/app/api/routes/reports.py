"""Report generation routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models import Site, UptimeCheck, SSLCheck, PerformanceCheck, SEOCheck
from app.api.routes.auth import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/site/{site_id}")
async def generate_site_report(
    site_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "json",  # json, html, pdf
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate a comprehensive report for a site"""
    # Get site
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Check permission
    if not current_user.is_superuser and site.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Parse dates
    if not end_date:
        end_datetime = datetime.utcnow()
    else:
        end_datetime = datetime.fromisoformat(end_date)
    
    if not start_date:
        start_datetime = end_datetime - timedelta(days=30)
    else:
        start_datetime = datetime.fromisoformat(start_date)
    
    # Gather data
    report_data = {
        "site": {
            "id": site.id,
            "name": site.name,
            "url": site.url,
            "platform": site.platform.value,
        },
        "period": {
            "start": start_datetime.isoformat(),
            "end": end_datetime.isoformat(),
        },
        "uptime": await get_uptime_summary(db, site_id, start_datetime, end_datetime),
        "ssl": await get_ssl_summary(db, site_id, start_datetime, end_datetime),
        "performance": await get_performance_summary(db, site_id, start_datetime, end_datetime),
        "seo": await get_seo_summary(db, site_id, start_datetime, end_datetime),
    }
    
    if format == "json":
        return report_data
    elif format == "html":
        # TODO: Generate HTML report
        return {"message": "HTML reports coming soon", "data": report_data}
    elif format == "pdf":
        # TODO: Generate PDF report
        return {"message": "PDF reports coming soon", "data": report_data}
    else:
        raise HTTPException(status_code=400, detail="Invalid format")


async def get_uptime_summary(db: Session, site_id: int, start: datetime, end: datetime):
    """Get uptime summary for date range"""
    checks = db.query(UptimeCheck).filter(
        UptimeCheck.site_id == site_id,
        UptimeCheck.checked_at >= start,
        UptimeCheck.checked_at <= end
    ).all()
    
    if not checks:
        return {"uptime_percentage": 0, "total_checks": 0, "downtime_incidents": 0}
    
    up_checks = sum(1 for c in checks if c.is_up)
    downtime_incidents = sum(1 for c in checks if not c.is_up)
    
    return {
        "uptime_percentage": (up_checks / len(checks)) * 100,
        "total_checks": len(checks),
        "downtime_incidents": downtime_incidents,
        "average_response_time": sum(c.response_time or 0 for c in checks) / len(checks) if checks else 0,
    }


async def get_ssl_summary(db: Session, site_id: int, start: datetime, end: datetime):
    """Get SSL summary for date range"""
    latest_check = db.query(SSLCheck).filter(
        SSLCheck.site_id == site_id,
        SSLCheck.checked_at >= start,
        SSLCheck.checked_at <= end
    ).order_by(SSLCheck.checked_at.desc()).first()
    
    if not latest_check:
        return {"status": "unknown"}
    
    return {
        "is_valid": latest_check.is_valid,
        "days_until_expiry": latest_check.days_until_expiry,
        "issuer": latest_check.issuer,
        "valid_until": latest_check.valid_until.isoformat() if latest_check.valid_until else None,
    }


async def get_performance_summary(db: Session, site_id: int, start: datetime, end: datetime):
    """Get performance summary for date range"""
    checks = db.query(PerformanceCheck).filter(
        PerformanceCheck.site_id == site_id,
        PerformanceCheck.checked_at >= start,
        PerformanceCheck.checked_at <= end
    ).all()
    
    if not checks:
        return {"average_load_time": 0, "total_checks": 0}
    
    return {
        "average_load_time": sum(c.load_time or 0 for c in checks) / len(checks),
        "average_performance_score": sum(c.performance_score or 0 for c in checks) / len(checks),
        "total_checks": len(checks),
    }


async def get_seo_summary(db: Session, site_id: int, start: datetime, end: datetime):
    """Get SEO summary for date range"""
    latest_check = db.query(SEOCheck).filter(
        SEOCheck.site_id == site_id,
        SEOCheck.checked_at >= start,
        SEOCheck.checked_at <= end
    ).order_by(SEOCheck.checked_at.desc()).first()
    
    if not latest_check:
        return {"seo_score": 0}
    
    return {
        "seo_score": latest_check.seo_score,
        "has_sitemap": latest_check.has_sitemap,
        "is_mobile_friendly": latest_check.is_mobile_friendly,
        "issues_count": len(latest_check.issues) if latest_check.issues else 0,
    }
