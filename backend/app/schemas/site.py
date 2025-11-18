from typing import Optional, List
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from enum import Enum


class SiteStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    INACTIVE = "inactive"


class SitePlatform(str, Enum):
    WORDPRESS = "wordpress"
    CUSTOM = "custom"
    STATIC = "static"
    OTHER = "other"


class SiteBase(BaseModel):
    name: str
    url: str
    platform: Optional[SitePlatform] = SitePlatform.WORDPRESS
    status: Optional[SiteStatus] = SiteStatus.ACTIVE

    # Monitoring configuration
    check_interval: Optional[int] = 300
    uptime_enabled: Optional[bool] = True
    ssl_enabled: Optional[bool] = True
    performance_enabled: Optional[bool] = True
    broken_links_enabled: Optional[bool] = True
    wordpress_checks_enabled: Optional[bool] = False
    seo_enabled: Optional[bool] = True

    # WordPress credentials
    wp_admin_url: Optional[str] = None
    wp_username: Optional[str] = None
    wp_password: Optional[str] = None
    wp_api_url: Optional[str] = None

    # Alert configuration
    alert_email: Optional[str] = None
    ntfy_topic: Optional[str] = None
    alert_threshold: Optional[int] = 1

    # Client information
    client_id: Optional[int] = None

    # Invoice Ninja integration
    invoice_ninja_client_id: Optional[str] = None

    # Metadata
    tags: Optional[List[str]] = []
    notes: Optional[str] = None


class SiteCreate(SiteBase):
    pass


class SiteUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    platform: Optional[SitePlatform] = None
    status: Optional[SiteStatus] = None
    check_interval: Optional[int] = None
    uptime_enabled: Optional[bool] = None
    ssl_enabled: Optional[bool] = None
    performance_enabled: Optional[bool] = None
    broken_links_enabled: Optional[bool] = None
    wordpress_checks_enabled: Optional[bool] = None
    seo_enabled: Optional[bool] = None
    wp_admin_url: Optional[str] = None
    wp_username: Optional[str] = None
    wp_password: Optional[str] = None
    wp_api_url: Optional[str] = None
    alert_email: Optional[str] = None
    ntfy_topic: Optional[str] = None
    alert_threshold: Optional[int] = None
    client_id: Optional[int] = None
    invoice_ninja_client_id: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class SiteInDBBase(SiteBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_checked_at: Optional[datetime] = None
    current_status_code: Optional[int] = None
    current_response_time: Optional[int] = None
    current_ssl_expiry: Optional[datetime] = None
    current_ssl_valid: Optional[bool] = True

    class Config:
        from_attributes = True


class Site(SiteInDBBase):
    pass


class SiteInDB(SiteInDBBase):
    pass
