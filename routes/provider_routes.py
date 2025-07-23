from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId
from models.provider import ProviderUpdate, ToggleAvailability
from services.auth_service import get_current_user
from handlers.provider_handler import (
    get_all_providers,
    get_provider_by_id,
    get_providers_by_service,
    toggle_provider_availability,
    update_provider_profile,
    get_top_rated_providers,
    get_providers_nearby,
    delete_provider
)

router = APIRouter()


@router.get("/", response_model=List[dict])
def list_all_providers():
    """Get all providers (no approval filter)"""
    return get_all_providers()


@router.get("/{provider_id}", response_model=dict)
def get_single_provider(provider_id: str):
    """Get provider details by ID"""
    provider = get_provider_by_id(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.get("/service/{service_id}", response_model=List[dict])
def filter_providers_by_service(service_id: str):
    """Get providers offering a specific service"""
    return get_providers_by_service(service_id)


@router.patch("/{provider_id}/availability", response_model=dict)
def update_availability(
        provider_id: str,
        availability: ToggleAvailability
):
    """Update provider availability status"""
    result = toggle_provider_availability(provider_id, availability.is_available)
    if result.modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Provider not found or no changes made"
        )
    return {"message": "Availability updated successfully"}


@router.patch("/{provider_id}", response_model=dict)
def update_provider_details(
        provider_id: str,
        update_data: ProviderUpdate
):
    """Update provider profile information"""
    result = update_provider_profile(
        provider_id,
        update_data.bio,
        update_data.experience_years,
        update_data.base_price,
        update_data.skills
    )
    if result.modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Provider not found or no updates provided"
        )
    return {"message": "Provider profile updated successfully"}


@router.get("/top-rated/", response_model=List[dict])
def list_top_rated_providers():
    """Get top rated providers"""
    return get_top_rated_providers()


@router.get("/nearby/{location}", response_model=List[dict])
def find_nearby_providers(location: str):
    """Find providers near a location"""
    return get_providers_nearby(location)


@router.delete("/{provider_id}", response_model=dict)
def remove_provider(
        provider_id: str,
        current_user: dict = Depends(get_current_user)
):
    """Delete a provider account (self or admin only)"""
    if current_user["_id"] != provider_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only the provider or admin can delete this account"
        )

    result = delete_provider(provider_id)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"message": "Provider account deleted successfully"}