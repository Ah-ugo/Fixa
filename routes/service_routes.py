from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from typing import Optional
from typing import List, Optional
from models.service import ServiceCreate, ServiceUpdate, ServiceResponse
from services.auth_service import get_current_admin  # Ensure only admins can add/update/delete services
from db import services_collection
from bson import ObjectId
from handlers.service_handler import get_services, get_service_by_id, add_service, update_service, delete_service

router = APIRouter()


@router.get("/", response_model=List[ServiceResponse])
def fetch_services():
    """Retrieve a list of available services."""
    return get_services()


@router.get("/{service_id}", response_model=ServiceResponse)
def fetch_service_by_id(service_id: str):
    """Retrieve details of a specific service."""
    service = get_service_by_id(service_id)
    if "error" in service:
        raise HTTPException(status_code=404, detail=service["error"])
    return service


@router.post("/", response_model=dict)
def create_service(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: Optional[UploadFile] = File(None),
    admin: dict = Depends(get_current_admin)
):
    """Add a new service (Admin only)."""
    return add_service(name, description, price, image)


@router.put("/{service_id}", response_model=dict)
def modify_service(service_id: str, service: ServiceUpdate, admin: dict = Depends(get_current_admin)):
    """Update service details (Admin only)."""
    return update_service(service_id, service.name, service.description, service.price, service.image)


@router.delete("/{service_id}", response_model=dict)
def remove_service(service_id: str, admin: dict = Depends(get_current_admin)):
    """Delete a service (Admin only)."""
    return delete_service(service_id)
