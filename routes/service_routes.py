from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File,Body
from typing import Optional
from typing import List, Optional
from models.service import ServiceCreate, ServiceUpdate, ServiceResponse
from services.auth_service import get_current_admin, get_current_user
from db import services_collection
from bson import ObjectId

from handlers.service_handler import get_services, get_service_by_id, add_service, update_service, delete_service, add_services_to_provider, remove_services_from_provider, get_provider_services

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


@router.post("/add_provider_services", response_model=dict)
async def add_provider_services(
        provider_id: str,
        service_ids: List[str] = Body(..., embed=True),
        current_user: dict = Depends(get_current_user)
):
    """Add services to a provider's offerings"""
    # Authorization check
    if str(current_user["_id"]) != provider_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only the provider or admin can modify services"
        )

    result = add_services_to_provider(provider_id, service_ids)
    if "error" in result:
        raise HTTPException(
            status_code=400 if "format" in result["error"] else 404,
            detail=result["error"]
        )
    return {"message": f"Added {result['modified_count']} services"}


@router.delete("/remove_provider_services", response_model=dict)
async def remove_provider_services(
        provider_id: str,
        service_ids: List[str] = Body(..., embed=True),
        current_user: dict = Depends(get_current_user)
):
    """Remove services from a provider's offerings"""
    # Authorization check
    if str(current_user["_id"]) != provider_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only the provider or admin can modify services"
        )

    result = remove_services_from_provider(provider_id, service_ids)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"message": f"Removed {result['modified_count']} services"}


@router.get("/provider/{provider_id}", response_model=List[dict])
async def list_provider_services(provider_id: str):
    """List all services offered by a provider with full details"""
    services = get_provider_services(provider_id)
    if isinstance(services, dict) and "error" in services:
        raise HTTPException(
            status_code=400 if "format" in services["error"] else 404,
            detail=services["error"]
        )
    return services