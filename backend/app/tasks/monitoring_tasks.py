"""Celery tasks for site monitoring"""
import logging
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models import Site, UptimeCheck, SSLCheck, PerformanceCheck, BrokenLinkCheck, WordPressCheck, SEOCheck, Alert
from app.models.site import SiteStatus
from app.models.alert import AlertType, AlertSeverity, AlertStatus
from app.services import (
    uptime_monitor,
    ssl_monitor,
    performance_monitor,
    broken_links_monitor,
    wordpress_monitor,
    seo_monitor,
    ntfy_service
)
from app.core.config import settings
import asyncio

logger = logging.getLogger(__name__)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, will be closed in task


@celery_app.task(name="app.tasks.monitoring_tasks.check_all_sites")
def check_all_sites():
    """Check all active sites"""
    db = get_db()
    try:
        # Get all active sites
        sites = db.query(Site).filter(Site.status == SiteStatus.ACTIVE).all()
        
        logger.info(f"Checking {len(sites)} active sites")
        
        for site in sites:
            # Check if it's time to check this site
            if should_check_site(site):
                check_site.delay(site.id)
        
    except Exception as e:
        logger.error(f"Error in check_all_sites: {str(e)}")
    finally:
        db.close()


@celery_app.task(name="app.tasks.monitoring_tasks.check_site")
def check_site(site_id: int):
    """Perform all checks for a single site"""
    db = get_db()
    try:
        site = db.query(Site).filter(Site.id == site_id).first()
        if not site:
            logger.error(f"Site {site_id} not found")
            return
        
        logger.info(f"Checking site: {site.name} ({site.url})")
        
        # Run checks asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Uptime check
            if site.uptime_enabled:
                uptime_result = loop.run_until_complete(uptime_monitor.check_uptime(site.url))
                save_uptime_check(db, site.id, uptime_result)
                
                # Create alert if site is down
                if not uptime_result.get("is_up"):
                    create_alert(
                        db,
                        site,
                        AlertType.UPTIME,
                        AlertSeverity.CRITICAL,
                        f"Site {site.name} is down",
                        f"Status code: {uptime_result.get('status_code')}, Error: {uptime_result.get('error_message')}"
                    )
            
            # SSL check
            if site.ssl_enabled and site.url.startswith('https'):
                ssl_result = loop.run_until_complete(ssl_monitor.check_ssl_certificate(site.url))
                save_ssl_check(db, site.id, ssl_result)
                
                # Create alert if SSL is expiring soon
                if ssl_result.get("days_until_expiry") and ssl_result["days_until_expiry"] < settings.SSL_WARNING_DAYS:
                    create_alert(
                        db,
                        site,
                        AlertType.SSL,
                        AlertSeverity.WARNING,
                        f"SSL certificate expiring soon for {site.name}",
                        f"Certificate expires in {ssl_result['days_until_expiry']} days"
                    )
            
            # Performance check
            if site.performance_enabled:
                perf_result = loop.run_until_complete(performance_monitor.check_performance(site.url))
                save_performance_check(db, site.id, perf_result)
                
                # Create alert if performance is poor
                if perf_result.get("load_time") and perf_result["load_time"] > settings.PERFORMANCE_THRESHOLD:
                    create_alert(
                        db,
                        site,
                        AlertType.PERFORMANCE,
                        AlertSeverity.WARNING,
                        f"Slow page load for {site.name}",
                        f"Load time: {perf_result['load_time']}ms (threshold: {settings.PERFORMANCE_THRESHOLD}ms)"
                    )
            
            # Broken links check (less frequent)
            if site.broken_links_enabled:
                broken_links_result = loop.run_until_complete(broken_links_monitor.check_broken_links(site.url))
                save_broken_links_check(db, site.id, broken_links_result)
                
                # Create alert if broken links found
                if broken_links_result.get("broken_links", 0) > 0:
                    create_alert(
                        db,
                        site,
                        AlertType.BROKEN_LINKS,
                        AlertSeverity.WARNING,
                        f"Broken links found on {site.name}",
                        f"{broken_links_result['broken_links']} broken links out of {broken_links_result['total_links']} total"
                    )
            
            # WordPress check (if enabled)
            if site.wordpress_checks_enabled:
                wp_result = loop.run_until_complete(wordpress_monitor.check_wordpress(site.url))
                save_wordpress_check(db, site.id, wp_result)
                
                # Create alert if updates available
                total_updates = wp_result.get("plugins_need_update", 0) + wp_result.get("themes_need_update", 0)
                if wp_result.get("wp_update_available") or total_updates > 0:
                    create_alert(
                        db,
                        site,
                        AlertType.WORDPRESS,
                        AlertSeverity.INFO,
                        f"WordPress updates available for {site.name}",
                        f"Core update: {wp_result.get('wp_update_available')}, Plugins: {wp_result.get('plugins_need_update')}, Themes: {wp_result.get('themes_need_update')}"
                    )
            
            # SEO check (less frequent)
            if site.seo_enabled:
                seo_result = loop.run_until_complete(seo_monitor.check_seo(site.url))
                save_seo_check(db, site.id, seo_result)
                
                # Create alert if SEO score is low
                if seo_result.get("seo_score", 100) < 50:
                    create_alert(
                        db,
                        site,
                        AlertType.SEO,
                        AlertSeverity.WARNING,
                        f"Low SEO score for {site.name}",
                        f"SEO score: {seo_result['seo_score']}/100"
                    )
            
            # Update site's last checked timestamp
            site.last_checked_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Completed checks for site: {site.name}")
        
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Error checking site {site_id}: {str(e)}")
        db.rollback()
    finally:
        db.close()


@celery_app.task(name="app.tasks.monitoring_tasks.cleanup_old_data")
def cleanup_old_data():
    """Clean up old monitoring data (older than 90 days)"""
    db = get_db()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        # Delete old uptime checks
        deleted_uptime = db.query(UptimeCheck).filter(UptimeCheck.checked_at < cutoff_date).delete()
        deleted_ssl = db.query(SSLCheck).filter(SSLCheck.checked_at < cutoff_date).delete()
        deleted_perf = db.query(PerformanceCheck).filter(PerformanceCheck.checked_at < cutoff_date).delete()
        deleted_broken_links = db.query(BrokenLinkCheck).filter(BrokenLinkCheck.checked_at < cutoff_date).delete()
        deleted_wp = db.query(WordPressCheck).filter(WordPressCheck.checked_at < cutoff_date).delete()
        deleted_seo = db.query(SEOCheck).filter(SEOCheck.checked_at < cutoff_date).delete()
        
        # Delete resolved alerts older than 30 days
        alert_cutoff = datetime.utcnow() - timedelta(days=30)
        deleted_alerts = db.query(Alert).filter(
            Alert.status == AlertStatus.RESOLVED,
            Alert.resolved_at < alert_cutoff
        ).delete()
        
        db.commit()
        
        logger.info(
            f"Cleaned up old data: {deleted_uptime} uptime, {deleted_ssl} SSL, "
            f"{deleted_perf} performance, {deleted_broken_links} broken links, "
            f"{deleted_wp} WordPress, {deleted_seo} SEO checks, {deleted_alerts} alerts"
        )
    
    except Exception as e:
        logger.error(f"Error cleaning up old data: {str(e)}")
        db.rollback()
    finally:
        db.close()


def should_check_site(site: Site) -> bool:
    """Determine if a site should be checked now based on its check interval"""
    if not site.last_checked_at:
        return True
    
    time_since_last_check = (datetime.utcnow() - site.last_checked_at).total_seconds()
    return time_since_last_check >= site.check_interval


def save_uptime_check(db: Session, site_id: int, result: dict):
    """Save uptime check result to database"""
    check = UptimeCheck(
        site_id=site_id,
        status_code=result.get("status_code"),
        response_time=result.get("response_time"),
        is_up=result.get("is_up", False),
        error_message=result.get("error_message"),
        headers=result.get("headers"),
        redirect_url=result.get("redirect_url"),
    )
    db.add(check)
    db.commit()


def save_ssl_check(db: Session, site_id: int, result: dict):
    """Save SSL check result to database"""
    check = SSLCheck(
        site_id=site_id,
        is_valid=result.get("is_valid", True),
        issuer=result.get("issuer"),
        subject=result.get("subject"),
        valid_from=result.get("valid_from"),
        valid_until=result.get("valid_until"),
        days_until_expiry=result.get("days_until_expiry"),
        error_message=result.get("error_message"),
        certificate_chain=result.get("certificate_chain"),
    )
    db.add(check)
    db.commit()


def save_performance_check(db: Session, site_id: int, result: dict):
    """Save performance check result to database"""
    check = PerformanceCheck(
        site_id=site_id,
        load_time=result.get("load_time"),
        time_to_first_byte=result.get("time_to_first_byte"),
        dom_load_time=result.get("dom_load_time"),
        page_size=result.get("page_size"),
        num_requests=result.get("num_requests"),
        num_css=result.get("num_css"),
        num_js=result.get("num_js"),
        num_images=result.get("num_images"),
        performance_score=result.get("performance_score"),
    )
    db.add(check)
    db.commit()


def save_broken_links_check(db: Session, site_id: int, result: dict):
    """Save broken links check result to database"""
    check = BrokenLinkCheck(
        site_id=site_id,
        total_links=result.get("total_links", 0),
        broken_links=result.get("broken_links", 0),
        broken_link_details=result.get("broken_link_details"),
        internal_links=result.get("internal_links", 0),
        external_links=result.get("external_links", 0),
    )
    db.add(check)
    db.commit()


def save_wordpress_check(db: Session, site_id: int, result: dict):
    """Save WordPress check result to database"""
    check = WordPressCheck(
        site_id=site_id,
        wp_version=result.get("wp_version"),
        wp_latest_version=result.get("wp_latest_version"),
        wp_update_available=result.get("wp_update_available", False),
        plugins_total=result.get("plugins_total", 0),
        plugins_need_update=result.get("plugins_need_update", 0),
        plugin_details=result.get("plugin_details"),
        themes_total=result.get("themes_total", 0),
        themes_need_update=result.get("themes_need_update", 0),
        theme_details=result.get("theme_details"),
        security_issues=result.get("security_issues"),
        security_score=result.get("security_score"),
        php_version=result.get("php_version"),
        mysql_version=result.get("mysql_version"),
    )
    db.add(check)
    db.commit()


def save_seo_check(db: Session, site_id: int, result: dict):
    """Save SEO check result to database"""
    check = SEOCheck(
        site_id=site_id,
        title=result.get("title"),
        title_length=result.get("title_length", 0),
        meta_description=result.get("meta_description"),
        meta_description_length=result.get("meta_description_length", 0),
        h1_tags=result.get("h1_tags"),
        h1_count=result.get("h1_count", 0),
        h2_count=result.get("h2_count", 0),
        word_count=result.get("word_count", 0),
        images_total=result.get("images_total", 0),
        images_without_alt=result.get("images_without_alt", 0),
        internal_links=result.get("internal_links", 0),
        external_links=result.get("external_links", 0),
        has_robots_txt=result.get("has_robots_txt", False),
        has_sitemap=result.get("has_sitemap", False),
        is_mobile_friendly=result.get("is_mobile_friendly", False),
        has_schema_markup=result.get("has_schema_markup", False),
        has_og_tags=result.get("has_og_tags", False),
        has_twitter_tags=result.get("has_twitter_tags", False),
        seo_score=result.get("seo_score", 0),
        issues=result.get("issues"),
    )
    db.add(check)
    db.commit()


def create_alert(
    db: Session,
    site: Site,
    alert_type: AlertType,
    severity: AlertSeverity,
    title: str,
    message: str
):
    """Create an alert and send notifications"""
    # Check if similar alert already exists and is open
    existing_alert = db.query(Alert).filter(
        Alert.site_id == site.id,
        Alert.alert_type == alert_type,
        Alert.status == AlertStatus.OPEN
    ).first()
    
    if existing_alert:
        # Alert already exists, don't create duplicate
        return
    
    # Create new alert
    alert = Alert(
        site_id=site.id,
        alert_type=alert_type,
        severity=severity,
        status=AlertStatus.OPEN,
        title=title,
        message=message,
    )
    db.add(alert)
    db.commit()
    
    # Send notifications asynchronously
    send_alert_notifications.delay(alert.id)


@celery_app.task(name="app.tasks.monitoring_tasks.send_alert_notifications")
def send_alert_notifications(alert_id: int):
    """Send alert notifications via NTFY and email"""
    db = get_db()
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return
        
        site = alert.site
        
        # Send NTFY notification
        if settings.NTFY_ENABLED:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(
                    ntfy_service.send_alert(
                        site_name=site.name,
                        alert_type=alert.alert_type,
                        severity=alert.severity.value,
                        message=alert.message,
                        site_url=site.url,
                    )
                )
                
                if success:
                    alert.ntfy_sent = True
                    alert.ntfy_sent_at = datetime.utcnow()
                    db.commit()
            finally:
                loop.close()
        
        # TODO: Send email notification
        
    except Exception as e:
        logger.error(f"Error sending alert notifications for alert {alert_id}: {str(e)}")
    finally:
        db.close()
