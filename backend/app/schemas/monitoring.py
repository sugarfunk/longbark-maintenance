from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime


# Uptime Check Schemas
class UptimeCheckBase(BaseModel):
    site_id: int
    status_code: Optional[int] = None
    response_time: Optional[int] = None
    is_up: bool = True
    error_message: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None
    redirect_url: Optional[str] = None


class UptimeCheckInDB(UptimeCheckBase):
    id: int
    checked_at: datetime

    class Config:
        from_attributes = True


class UptimeCheck(UptimeCheckInDB):
    pass


# SSL Check Schemas
class SSLCheckBase(BaseModel):
    site_id: int
    is_valid: bool = True
    issuer: Optional[str] = None
    subject: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    days_until_expiry: Optional[int] = None
    error_message: Optional[str] = None
    certificate_chain: Optional[List[Dict[str, Any]]] = None


class SSLCheckInDB(SSLCheckBase):
    id: int
    checked_at: datetime

    class Config:
        from_attributes = True


class SSLCheck(SSLCheckInDB):
    pass


# Performance Check Schemas
class PerformanceCheckBase(BaseModel):
    site_id: int
    load_time: Optional[int] = None
    time_to_first_byte: Optional[int] = None
    dom_load_time: Optional[int] = None
    page_size: Optional[int] = None
    num_requests: Optional[int] = None
    num_css: Optional[int] = None
    num_js: Optional[int] = None
    num_images: Optional[int] = None
    performance_score: Optional[int] = None


class PerformanceCheckInDB(PerformanceCheckBase):
    id: int
    checked_at: datetime

    class Config:
        from_attributes = True


class PerformanceCheck(PerformanceCheckInDB):
    pass


# Broken Link Check Schemas
class BrokenLinkCheckBase(BaseModel):
    site_id: int
    total_links: int = 0
    broken_links: int = 0
    broken_link_details: Optional[List[Dict[str, Any]]] = None
    internal_links: int = 0
    external_links: int = 0


class BrokenLinkCheckInDB(BrokenLinkCheckBase):
    id: int
    checked_at: datetime

    class Config:
        from_attributes = True


class BrokenLinkCheck(BrokenLinkCheckInDB):
    pass


# WordPress Check Schemas
class WordPressCheckBase(BaseModel):
    site_id: int
    wp_version: Optional[str] = None
    wp_latest_version: Optional[str] = None
    wp_update_available: bool = False
    plugins_total: int = 0
    plugins_need_update: int = 0
    plugin_details: Optional[List[Dict[str, Any]]] = None
    themes_total: int = 0
    themes_need_update: int = 0
    theme_details: Optional[List[Dict[str, Any]]] = None
    security_issues: Optional[List[Dict[str, Any]]] = None
    security_score: Optional[int] = None
    php_version: Optional[str] = None
    mysql_version: Optional[str] = None


class WordPressCheckInDB(WordPressCheckBase):
    id: int
    checked_at: datetime

    class Config:
        from_attributes = True


class WordPressCheck(WordPressCheckInDB):
    pass
