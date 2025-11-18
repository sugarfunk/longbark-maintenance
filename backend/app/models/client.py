from sqlalchemy import Boolean, Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    company = Column(String, nullable=True)
    
    # Invoice Ninja integration
    invoice_ninja_id = Column(String, unique=True, nullable=True, index=True)
    invoice_ninja_data = Column(JSON, nullable=True)
    
    # Client portal access
    portal_enabled = Column(Boolean, default=False)
    portal_username = Column(String, unique=True, nullable=True)
    portal_password_hash = Column(String, nullable=True)
    
    # Contact information
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    country = Column(String, nullable=True)
    
    # Metadata
    notes = Column(String, nullable=True)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sites = relationship("Site", back_populates="client")
