from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SEOCheck(Base):
    __tablename__ = "seo_checks"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    
    # Page title and meta
    title = Column(String, nullable=True)
    title_length = Column(Integer, nullable=True)
    meta_description = Column(String, nullable=True)
    meta_description_length = Column(Integer, nullable=True)
    
    # Headers
    h1_tags = Column(JSON, nullable=True)  # List of H1 tags
    h1_count = Column(Integer, default=0)
    h2_count = Column(Integer, default=0)
    
    # Content analysis
    word_count = Column(Integer, default=0)
    
    # Images
    images_total = Column(Integer, default=0)
    images_without_alt = Column(Integer, default=0)
    
    # Links
    internal_links = Column(Integer, default=0)
    external_links = Column(Integer, default=0)
    
    # Technical SEO
    has_robots_txt = Column(Boolean, default=False)
    has_sitemap = Column(Boolean, default=False)
    is_mobile_friendly = Column(Boolean, default=False)
    has_schema_markup = Column(Boolean, default=False)
    
    # Social meta tags
    has_og_tags = Column(Boolean, default=False)
    has_twitter_tags = Column(Boolean, default=False)
    
    # SEO score
    seo_score = Column(Integer, nullable=True)  # 0-100
    
    # Issues
    issues = Column(JSON, nullable=True)  # List of SEO issues found
    
    checked_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    site = relationship("Site", back_populates="seo_checks")


class KeywordRanking(Base):
    __tablename__ = "keyword_rankings"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    
    # Keyword details
    keyword = Column(String, nullable=False, index=True)
    search_engine = Column(String, default="google")  # google, bing, etc.
    location = Column(String, nullable=True)  # Geographic location
    language = Column(String, default="en")
    
    # Ranking data
    position = Column(Integer, nullable=True)
    url = Column(String, nullable=True)  # The URL that ranks for this keyword
    
    # Search volume and metrics
    search_volume = Column(Integer, nullable=True)
    difficulty = Column(Integer, nullable=True)  # 0-100
    
    # Change tracking
    previous_position = Column(Integer, nullable=True)
    position_change = Column(Integer, nullable=True)
    
    checked_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    site = relationship("Site", back_populates="keyword_rankings")


class Backlink(Base):
    __tablename__ = "backlinks"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    
    # Backlink details
    source_url = Column(String, nullable=False)
    source_domain = Column(String, nullable=False, index=True)
    target_url = Column(String, nullable=False)
    anchor_text = Column(String, nullable=True)
    
    # Link attributes
    is_follow = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
    # Domain metrics
    domain_authority = Column(Integer, nullable=True)  # 0-100
    page_authority = Column(Integer, nullable=True)  # 0-100
    
    # Discovery
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    site = relationship("Site", back_populates="backlinks")
