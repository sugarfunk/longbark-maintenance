from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UptimeCheck(Base):
    __tablename__ = "uptime_checks"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    
    # Check results
    status_code = Column(Integer, nullable=True)
    response_time = Column(Integer, nullable=True)  # milliseconds
    is_up = Column(Boolean, default=True)
    error_message = Column(String, nullable=True)
    
    # Response details
    headers = Column(JSON, nullable=True)
    redirect_url = Column(String, nullable=True)
    
    checked_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    site = relationship("Site", back_populates="uptime_checks")


class SSLCheck(Base):
    __tablename__ = "ssl_checks"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    
    # SSL Certificate details
    is_valid = Column(Boolean, default=True)
    issuer = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    days_until_expiry = Column(Integer, nullable=True)
    
    # SSL errors
    error_message = Column(String, nullable=True)
    certificate_chain = Column(JSON, nullable=True)
    
    checked_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    site = relationship("Site", back_populates="ssl_checks")


class PerformanceCheck(Base):
    __tablename__ = "performance_checks"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    
    # Performance metrics
    load_time = Column(Integer, nullable=True)  # milliseconds
    time_to_first_byte = Column(Integer, nullable=True)  # milliseconds
    dom_load_time = Column(Integer, nullable=True)  # milliseconds
    page_size = Column(Integer, nullable=True)  # bytes
    
    # Resource counts
    num_requests = Column(Integer, nullable=True)
    num_css = Column(Integer, nullable=True)
    num_js = Column(Integer, nullable=True)
    num_images = Column(Integer, nullable=True)
    
    # Performance score (0-100)
    performance_score = Column(Integer, nullable=True)
    
    checked_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    site = relationship("Site", back_populates="performance_checks")


class BrokenLinkCheck(Base):
    __tablename__ = "broken_link_checks"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    
    # Check results
    total_links = Column(Integer, default=0)
    broken_links = Column(Integer, default=0)
    broken_link_details = Column(JSON, nullable=True)  # List of broken links with status codes
    
    # Link types
    internal_links = Column(Integer, default=0)
    external_links = Column(Integer, default=0)
    
    checked_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    site = relationship("Site", back_populates="broken_link_checks")


class WordPressCheck(Base):
    __tablename__ = "wordpress_checks"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    
    # WordPress version
    wp_version = Column(String, nullable=True)
    wp_latest_version = Column(String, nullable=True)
    wp_update_available = Column(Boolean, default=False)
    
    # Plugin updates
    plugins_total = Column(Integer, default=0)
    plugins_need_update = Column(Integer, default=0)
    plugin_details = Column(JSON, nullable=True)  # List of plugins with update info
    
    # Theme updates
    themes_total = Column(Integer, default=0)
    themes_need_update = Column(Integer, default=0)
    theme_details = Column(JSON, nullable=True)
    
    # Security
    security_issues = Column(JSON, nullable=True)
    security_score = Column(Integer, nullable=True)  # 0-100
    
    # Metadata
    php_version = Column(String, nullable=True)
    mysql_version = Column(String, nullable=True)
    
    checked_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    site = relationship("Site", back_populates="wordpress_checks")
