from db import users_collection, services_collection
from typing import List, Optional
from bson import ObjectId
from handlers.service_handler import (
    add_services_to_provider,
    remove_services_from_provider,
    get_provider_services,
serialize_service
)

def serialize_provider(provider):
    """Convert MongoDB document to serializable format"""
    if provider and '_id' in provider:
        provider['_id'] = str(provider['_id'])
    return provider

def get_all_providers() -> List[dict]:
    """Get all providers with their services"""
    providers = users_collection.find(
        {"role": "provider"},
        {"password": 0}
    )
    result = []
    for provider in providers:
        provider = serialize_provider(provider)
        # Get full service details for the provider
        if 'services_offered' in provider:
            try:
                service_ids = [ObjectId(id) for id in provider['services_offered']]
                services = services_collection.find({"_id": {"$in": service_ids}})
                provider['services'] = [serialize_service(s) for s in services]
            except:
                provider['services'] = []
        else:
            provider['services'] = []
        result.append(provider)
    return result


def get_provider_by_id(provider_id: str):
    """Get single provider with their services"""
    provider = users_collection.find_one(
        {"_id": ObjectId(provider_id), "role": "provider"},
        {"password": 0}
    )
    if not provider:
        return None

    provider = serialize_provider(provider)
    # Get full service details for the provider
    if 'services_offered' in provider:
        service_ids = [ObjectId(id) for id in provider['services_offered']]
        services = services_collection.find({"_id": {"$in": service_ids}})
        provider['services'] = [serialize_service(s) for s in services]
    else:
        provider['services'] = []

    return provider

def get_providers_by_service(service_id: str):
    """Get providers offering a specific service"""
    try:
        # Convert service_id to ObjectId for consistent comparison
        service_obj_id = ObjectId(service_id)
        # Find providers that have this service in their services_offered array
        providers = users_collection.find(
            {
                "role": "provider",
                "services_offered": service_obj_id  # Compare ObjectId to ObjectId
            },
            {"password": 0}
        )
        return [serialize_provider(p) for p in providers]
    except Exception as e:
        print(f"Error in get_providers_by_service: {str(e)}")
        return []

def toggle_provider_availability(provider_id: str, is_available: bool):
    """Toggle provider's availability status"""
    return users_collection.update_one(
        {"_id": ObjectId(provider_id), "role": "provider"},
        {"$set": {"is_available": is_available}}
    )

def update_provider_profile(
    provider_id: str,
    bio: Optional[str] = None,
    experience_years: Optional[int] = None,
    base_price: Optional[float] = None,
    skills: Optional[List[str]] = None
):
    """Update provider profile information"""
    update_data = {}
    if bio is not None:
        update_data["bio"] = bio
    if experience_years is not None:
        update_data["experience_years"] = experience_years
    if base_price is not None:
        update_data["base_price"] = base_price
    if skills is not None:
        update_data["skills"] = skills

    if not update_data:
        return {"modified_count": 0}

    return users_collection.update_one(
        {"_id": ObjectId(provider_id), "role": "provider"},
        {"$set": update_data}
    )

def get_top_rated_providers(limit: int = 10):
    """Get top rated providers sorted by rating"""
    providers = users_collection.find(
        {"role": "provider"}
    ).sort("rating", -1).limit(limit)
    return [serialize_provider(p) for p in providers]

def get_providers_nearby(location: str):
    """Find providers near a location"""
    providers = users_collection.find(
        {
            "role": "provider",
            "address": {"$regex": location, "$options": "i"}
        },
        {"password": 0}
    )
    return [serialize_provider(p) for p in providers]

def delete_provider(provider_id: str):
    """Delete a provider account"""
    return users_collection.delete_one(
        {"_id": ObjectId(provider_id), "role": "provider"}
    )