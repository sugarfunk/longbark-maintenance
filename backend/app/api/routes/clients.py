from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User as UserModel
from app.models.client import Client as ClientModel
from app.models.site import Site as SiteModel
from app.schemas.client import Client, ClientCreate, ClientUpdate
from app.schemas.site import Site
from app.api.routes.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[Client])
def list_clients(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
) -> Any:
    """
    Retrieve clients with optional filters.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **search**: Search by client name, email, or company
    """
    query = db.query(ClientModel)

    # Apply search filter
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                ClientModel.name.ilike(search_filter),
                ClientModel.email.ilike(search_filter),
                ClientModel.company.ilike(search_filter),
            )
        )

    clients = query.offset(skip).limit(limit).all()
    return clients


@router.post("/", response_model=Client, status_code=status.HTTP_201_CREATED)
def create_client(
    *,
    db: Session = Depends(get_db),
    client_in: ClientCreate,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Create new client.
    """
    # Check if client with same email already exists
    if client_in.email:
        existing_client = (
            db.query(ClientModel).filter(ClientModel.email == client_in.email).first()
        )
        if existing_client:
            raise HTTPException(
                status_code=400,
                detail="A client with this email already exists.",
            )

    # Check if invoice_ninja_id is unique if provided
    if client_in.invoice_ninja_id:
        existing_client = (
            db.query(ClientModel)
            .filter(ClientModel.invoice_ninja_id == client_in.invoice_ninja_id)
            .first()
        )
        if existing_client:
            raise HTTPException(
                status_code=400,
                detail="A client with this Invoice Ninja ID already exists.",
            )

    # Check if portal username is unique if provided
    if client_in.portal_username:
        existing_client = (
            db.query(ClientModel)
            .filter(ClientModel.portal_username == client_in.portal_username)
            .first()
        )
        if existing_client:
            raise HTTPException(
                status_code=400,
                detail="A client with this portal username already exists.",
            )

    # Prepare client data
    client_data = client_in.model_dump(exclude={"portal_password"})

    # Hash portal password if provided
    if client_in.portal_password:
        client_data["portal_password_hash"] = get_password_hash(client_in.portal_password)

    # Create client
    client = ClientModel(**client_data)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/{client_id}", response_model=Client)
def get_client(
    *,
    db: Session = Depends(get_db),
    client_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Get client by ID.
    """
    client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return client


@router.put("/{client_id}", response_model=Client)
def update_client(
    *,
    db: Session = Depends(get_db),
    client_id: int,
    client_in: ClientUpdate,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Update client.
    """
    client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Check if email is being changed and if it already exists
    if client_in.email and client_in.email != client.email:
        existing_client = (
            db.query(ClientModel).filter(ClientModel.email == client_in.email).first()
        )
        if existing_client:
            raise HTTPException(
                status_code=400,
                detail="A client with this email already exists.",
            )

    # Check if invoice_ninja_id is being changed and if it already exists
    if (
        client_in.invoice_ninja_id
        and client_in.invoice_ninja_id != client.invoice_ninja_id
    ):
        existing_client = (
            db.query(ClientModel)
            .filter(ClientModel.invoice_ninja_id == client_in.invoice_ninja_id)
            .first()
        )
        if existing_client:
            raise HTTPException(
                status_code=400,
                detail="A client with this Invoice Ninja ID already exists.",
            )

    # Check if portal username is being changed and if it already exists
    if (
        client_in.portal_username
        and client_in.portal_username != client.portal_username
    ):
        existing_client = (
            db.query(ClientModel)
            .filter(ClientModel.portal_username == client_in.portal_username)
            .first()
        )
        if existing_client:
            raise HTTPException(
                status_code=400,
                detail="A client with this portal username already exists.",
            )

    # Update client
    update_data = client_in.model_dump(exclude_unset=True, exclude={"portal_password"})

    # Hash portal password if provided
    if client_in.portal_password:
        update_data["portal_password_hash"] = get_password_hash(client_in.portal_password)

    for field, value in update_data.items():
        setattr(client, field, value)

    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    *,
    db: Session = Depends(get_db),
    client_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> None:
    """
    Delete client.

    Note: This will also affect all sites associated with this client.
    The sites will not be deleted, but their client_id will be set to NULL.
    """
    client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    db.delete(client)
    db.commit()


@router.post("/{client_id}/sync-invoice-ninja", response_model=Client)
def sync_invoice_ninja(
    *,
    db: Session = Depends(get_db),
    client_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Sync client data with Invoice Ninja.

    This endpoint fetches the latest client data from Invoice Ninja and updates
    the local client record.
    """
    client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    if not client.invoice_ninja_id:
        raise HTTPException(
            status_code=400,
            detail="Client is not linked to Invoice Ninja",
        )

    # TODO: Implement Invoice Ninja sync using the invoice_ninja_service
    # from app.services.invoice_ninja_service import InvoiceNinjaService
    # service = InvoiceNinjaService()
    # invoice_ninja_data = service.get_client(client.invoice_ninja_id)
    # client.invoice_ninja_data = invoice_ninja_data
    # Update other fields as needed

    # For now, just return the client
    return client


@router.get("/{client_id}/sites", response_model=List[Site])
def get_client_sites(
    *,
    db: Session = Depends(get_db),
    client_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """
    Get all sites for a client.

    - **client_id**: Client ID to get sites for
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    query = db.query(SiteModel).filter(SiteModel.client_id == client_id)

    # Non-superusers can only see their own sites
    if not current_user.is_superuser:
        query = query.filter(SiteModel.owner_id == current_user.id)

    sites = query.offset(skip).limit(limit).all()
    return sites
