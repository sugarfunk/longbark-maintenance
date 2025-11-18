from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class AlertType(str, Enum):
    UPTIME = "uptime"
    SSL = "ssl"
    PERFORMANCE = "performance"
    BROKEN_LINKS = "broken_links"
    WORDPRESS = "wordpress"
    SEO = "seo"
    KEYWORD = "keyword"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class AlertBase(BaseModel):
    site_id: int
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    details: Optional[Dict[str, Any]] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    resolution_notes: Optional[str] = None


class AlertAcknowledge(BaseModel):
    pass


class AlertResolve(BaseModel):
    resolution_notes: Optional[str] = None


class AlertInDBBase(AlertBase):
    id: int
    status: AlertStatus
    email_sent: bool
    email_sent_at: Optional[datetime] = None
    ntfy_sent: bool
    ntfy_sent_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    acknowledged_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Alert(AlertInDBBase):
    pass


class AlertInDB(AlertInDBBase):
    pass
