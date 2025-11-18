from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class SiteStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    INACTIVE = "inactive"


class SitePlatform(str, enum.Enum):
    WORDPRESS = "wordpress"
    CUSTOM = "custom"
    STATIC = "static"
    OTHER = "other"


class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False, index=True)
    platform = Column(Enum(SitePlatform), default=SitePlatform.WORDPRESS)
    status = Column(Enum(SiteStatus), default=SiteStatus.ACTIVE)
    
    # Monitoring configuration
    check_interval = Column(Integer, default=300)  # seconds
    uptime_enabled = Column(Boolean, default=True)
    ssl_enabled = Column(Boolean, default=True)
    performance_enabled = Column(Boolean, default=True)
    broken_links_enabled = Column(Boolean, default=True)
    wordpress_checks_enabled = Column(Boolean, default=False)
    seo_enabled = Column(Boolean, default=True)
    
    # WordPress credentials (encrypted)
    wp_admin_url = Column(String, nullable=True)
    wp_username = Column(String, nullable=True)
    wp_password = Column(String, nullable=True)  # Should be encrypted
    wp_api_url = Column(String, nullable=True)
    
    # Alert configuration
    alert_email = Column(String, nullable=True)
    ntfy_topic = Column(String, nullable=True)
    alert_threshold = Column(Integer, default=1)  # Number of failures before alert
    
    # Client information
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Invoice Ninja integration
    invoice_ninja_client_id = Column(String, nullable=True)
    
    # Metadata
    tags = Column(JSON, default=list)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Current status (denormalized for quick access)
    current_status_code = Column(Integer, nullable=True)
    current_response_time = Column(Integer, nullable=True)  # milliseconds
    current_ssl_expiry = Column(DateTime(timezone=True), nullable=True)
    current_ssl_valid = Column(Boolean, default=True)
    
    # Relationships
    owner = relationship("User", back_populates="owned_sites")
    client = relationship("Client", back_populates="sites")
    uptime_checks = relationship("UptimeCheck", back_populates="site", cascade="all, delete-orphan")
    ssl_checks = relationship("SSLCheck", back_populates="site", cascade="all, delete-orphan")
    performance_checks = relationship("PerformanceCheck", back_populates="site", cascade="all, delete-orphan")
    broken_link_checks = relationship("BrokenLinkCheck", back_populates="site", cascade="all, delete-orphan")
    wordpress_checks = relationship("WordPressCheck", back_populates="site", cascade="all, delete-orphan")
    seo_checks = relationship("SEOCheck", back_populates="site", cascade="all, delete-orphan")
    keyword_rankings = relationship("KeywordRanking", back_populates="site", cascade="all, delete-orphan")
    backlinks = relationship("Backlink", back_populates="site", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="site", cascade="all, delete-orphan")
