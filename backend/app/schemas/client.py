from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime


class ClientBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None

    # Invoice Ninja integration
    invoice_ninja_id: Optional[str] = None
    invoice_ninja_data: Optional[Dict[str, Any]] = None

    # Client portal access
    portal_enabled: Optional[bool] = False
    portal_username: Optional[str] = None

    # Contact information
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None

    # Metadata
    notes: Optional[str] = None
    tags: Optional[List[str]] = []


class ClientCreate(ClientBase):
    portal_password: Optional[str] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    invoice_ninja_id: Optional[str] = None
    invoice_ninja_data: Optional[Dict[str, Any]] = None
    portal_enabled: Optional[bool] = None
    portal_username: Optional[str] = None
    portal_password: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class ClientInDBBase(ClientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Client(ClientInDBBase):
    pass


class ClientInDB(ClientInDBBase):
    portal_password_hash: Optional[str] = None
