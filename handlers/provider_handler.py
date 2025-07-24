from db import users_collection, services_collection, reviews_collection
from typing import List, Optional, Dict, Any
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


def get_recent_reviews(provider_id: str, limit: int = 3) -> List[Dict]:
    """Get recent reviews for a provider"""
    reviews = list(reviews_collection.find(
        {"provider_id": provider_id}
    ).sort("created_at", -1).limit(limit))

    return [{
        "id": str(review["_id"]),
        "user_id": review["user_id"],
        "rating": review["rating"],
        "comment": review.get("comment"),
        "created_at": review["created_at"]
    } for review in reviews]


def get_all_providers() -> List[dict]:
    """Get all providers with their services and rating info"""
    providers = users_collection.find(
        {"role": "provider"},
        {"password": 0}
    )
    result = []
    for provider in providers:
        provider = serialize_provider(provider)
        # Get full service details
        if 'services_offered' in provider:
            try:
                service_ids = [ObjectId(id) for id in provider['services_offered']]
                services = services_collection.find({"_id": {"$in": service_ids}})
                provider['services'] = [serialize_service(s) for s in services]
            except:
                provider['services'] = []
        else:
            provider['services'] = []

        # Add rating information
        provider_id = str(provider['_id'])
        provider['rating_stats'] = get_provider_rating_stats(provider_id)
        provider['recent_reviews'] = get_recent_reviews(provider_id)

        result.append(provider)
    return result


def get_provider_by_id(provider_id: str):
    """Get single provider with their services and rating info"""
    provider = users_collection.find_one(
        {"_id": ObjectId(provider_id), "role": "provider"},
        {"password": 0}
    )
    if not provider:
        return None

    provider = serialize_provider(provider)

    # Get full service details
    if 'services_offered' in provider:
        service_ids = [ObjectId(id) for id in provider['services_offered']]
        services = services_collection.find({"_id": {"$in": service_ids}})
        provider['services'] = [serialize_service(s) for s in services]
    else:
        provider['services'] = []

    # Add rating information
    provider_id = str(provider['_id'])
    provider['rating_stats'] = get_provider_rating_stats(provider_id)
    provider['recent_reviews'] = get_recent_reviews(provider_id)

    return provider

def get_providers_by_service(service_id: str):
    """Get providers offering a specific service

    Args:
        service_id: The ID of the service to search for

    Returns:
        List of serialized provider documents

    Raises:
        InvalidId: If the service_id is not a valid ObjectId
    """
    try:
        # Validate service_id format first
        service_obj_id = ObjectId(service_id)

        # Check if service exists
        if not services_collection.find_one({"_id": service_obj_id}):
            return []

        # Find providers offering this service
        providers = users_collection.find(
            {
                "role": "provider",
                "services_offered": service_obj_id
            },
            {
                "password": 0,
                "services_offered": 0  # Exclude from response
            }
        )

        # Include service details in each provider's response
        service = services_collection.find_one(
            {"_id": service_obj_id},
            {"name": 1, "description": 1, "price": 1, "image": 1}
        )

        serialized_providers = []
        for provider in providers:
            provider = serialize_provider(provider)
            provider["service_details"] = serialize_service(service)
            serialized_providers.append(provider)

        return serialized_providers

    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid service ID format"
        )
    except Exception as e:
        print(f"Error in get_providers_by_service: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching providers"
        )


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


def get_provider_rating_stats(provider_id: str) -> Dict:
    """Get detailed rating statistics for a provider"""
    pipeline = [
        {"$match": {"provider_id": provider_id}},
        {"$group": {
            "_id": None,
            "average": {"$avg": "$rating"},
            "count": {"$sum": 1},
            "1_star": {"$sum": {"$cond": [{"$eq": ["$rating", 1]}, 1, 0]}},
            "2_star": {"$sum": {"$cond": [{"$eq": ["$rating", 2]}, 1, 0]}},
            "3_star": {"$sum": {"$cond": [{"$eq": ["$rating", 3]}, 1, 0]}},
            "4_star": {"$sum": {"$cond": [{"$eq": ["$rating", 4]}, 1, 0]}},
            "5_star": {"$sum": {"$cond": [{"$eq": ["$rating", 5]}, 1, 0]}}
        }}
    ]

    result = list(reviews_collection.aggregate(pipeline))

    if not result:
        return {
            "average": 0,
            "count": 0,
            "breakdown": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }

    return {
        "average": result[0]["average"],
        "count": result[0]["count"],
        "breakdown": {
            1: result[0]["1_star"],
            2: result[0]["2_star"],
            3: result[0]["3_star"],
            4: result[0]["4_star"],
            5: result[0]["5_star"]
        }
    }




def delete_provider(provider_id: str):
    """Delete a provider account"""
    return users_collection.delete_one(
        {"_id": ObjectId(provider_id), "role": "provider"}
    )