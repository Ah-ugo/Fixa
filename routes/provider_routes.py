from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId
from db import providers_collection
from models.provider import ProviderUpdate, ToggleAvailability, ProviderApproval
from services.auth_service import get_current_admin
from handlers.provider_handler import (  # Importing functions
    get_approved_providers,
    get_provider_by_id,
    get_providers_by_service,
    toggle_provider_availability,
    update_provider_profile,
    get_top_rated_providers,
    get_providers_nearby,
    approve_provider,
    delete_provider
)

router = APIRouter()


@router.get("/approved", response_model=List[dict])
def approved_providers():
    """Retrieve all approved providers"""
    return get_approved_providers()


@router.get("/{provider_id}", response_model=dict)
def provider_by_id(provider_id: str):
    """Retrieve provider details by ID"""
    provider = get_provider_by_id(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.get("/service/{service_id}", response_model=List[dict])
def providers_by_service(service_id: str):
    """Retrieve providers by service offered"""
    return get_providers_by_service(service_id)


@router.patch("/{provider_id}/availability", response_model=dict)
def provider_availability(provider_id: str, data: ToggleAvailability):
    """Toggle provider availability"""
    result = toggle_provider_availability(provider_id, data.is_available)
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Provider not found or no change made")
    return {"message": "Provider availability updated successfully"}


@router.patch("/{provider_id}/update", response_model=dict)
def provider_update(provider_id: str, data: ProviderUpdate):
    """Update provider profile details"""
    result = update_provider_profile(provider_id, data.bio, data.experience_years, data.base_price, data.skills)
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Provider not found or no changes made")
    return {"message": "Provider profile updated successfully"}


@router.get("/all/top-rated", response_model=List[dict])
def top_rated_providers():
    """Retrieve top-rated providers"""
    return get_top_rated_providers()


@router.get("/nearby/{user_location}", response_model=List[dict])
def providers_nearby(user_location: str):
    """Retrieve providers near a specified location"""
    return get_providers_nearby(user_location)


@router.patch("/approve", response_model=dict, dependencies=[Depends(get_current_admin)])
def provider_approval(data: ProviderApproval):
    """Approve provider registration (Admin only)"""
    result = approve_provider(data.provider_id)
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Provider not found or already approved")
    return {"message": "Provider approved successfully"}


@router.delete("/{provider_id}", response_model=dict, dependencies=[Depends(get_current_admin)])
def provider_deletion(provider_id: str):
    """Delete a provider (Admin only)"""
    result = delete_provider(provider_id)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"message": "Provider deleted successfully"}
