from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class AlertType(str, enum.Enum):
    UPTIME = "uptime"
    SSL = "ssl"
    PERFORMANCE = "performance"
    BROKEN_LINKS = "broken_links"
    WORDPRESS = "wordpress"
    SEO = "seo"
    KEYWORD = "keyword"


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    
    # Alert details
    alert_type = Column(Enum(AlertType), nullable=False, index=True)
    severity = Column(Enum(AlertSeverity), nullable=False, index=True)
    status = Column(Enum(AlertStatus), default=AlertStatus.OPEN, index=True)
    
    # Message
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    
    # Notification tracking
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime(timezone=True), nullable=True)
    ntfy_sent = Column(Boolean, default=False)
    ntfy_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Resolution
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    site = relationship("Site", back_populates="alerts")
