from db import services_collection, users_collection
from bson import ObjectId
from typing import Optional, List, Dict, Union, Any
from services.cloudinary_service import upload_image
from fastapi import UploadFile


def serialize_service(service):
    if service and '_id' in service:
        service['_id'] = str(service['_id'])
    return service


def add_services_to_provider(provider_id: str, service_ids: List[str]) -> Dict[str, Union[int, str]]:
    """Add services to a provider's offerings with validation"""
    # Convert to ObjectId for query
    try:
        service_object_ids = [ObjectId(id) for id in service_ids]
    except:
        return {"error": "Invalid service ID format"}

    # Verify all services exist
    existing_count = services_collection.count_documents({
        "_id": {"$in": service_object_ids}
    })
    if existing_count != len(service_ids):
        return {"error": "One or more services not found"}

    result = users_collection.update_one(
        {"_id": ObjectId(provider_id), "role": "provider"},
        {"$addToSet": {"services_offered": {"$each": service_ids}}}
    )

    if result.matched_count == 0:
        return {"error": "Provider not found"}
    return {"modified_count": result.modified_count}


def remove_services_from_provider(provider_id: str, service_ids: List[str]) -> Dict[str, Union[int, str]]:
    """Remove services from a provider's offerings"""
    result = users_collection.update_one(
        {"_id": ObjectId(provider_id), "role": "provider"},
        {"$pull": {"services_offered": {"$in": service_ids}}}
    )

    if result.matched_count == 0:
        return {"error": "Provider not found"}
    return {"modified_count": result.modified_count}


def get_provider_services(provider_id: str) -> Union[List[Dict], Dict[str, str]]:
    """Get all services offered by a provider with full service details"""
    provider = users_collection.find_one(
        {"_id": ObjectId(provider_id), "role": "provider"},
        {"services_offered": 1}
    )
    if not provider:
        return {"error": "Provider not found"}

    try:
        service_ids = [ObjectId(id) for id in provider.get("services_offered", [])]
    except:
        return {"error": "Invalid service ID format in provider record"}

    services = services_collection.find({"_id": {"$in": service_ids}})
    return [serialize_service(s) for s in services]

# Get list of available services
def get_services():
    services = list(services_collection.find())
    for service in services:
        service["_id"] = str(service["_id"])
    return services


# Get details of a specific service
def get_service_by_id(service_id: str):
    service = services_collection.find_one({"_id": ObjectId(service_id)})
    if not service:
        return {"error": "Service not found"}

    # Convert ObjectId to string for JSON serialization
    service["_id"] = str(service["_id"])
    return service

# Add a new service (Admin only)
def add_service(name: str, description: str, price: float, image: Optional[UploadFile]):
    """Adds a new service to the database."""

    image_url = None
    if image:
        # Upload image to Cloudinary
        cloudinary_response = upload_image(image.file)
        image_url = cloudinary_response

    service_data = {
        "name": name,
        "description": description,
        "price": price,
        "image": image_url
    }

    # Save to DB (assuming `services_collection` exists)
    result = services_collection.insert_one(service_data)

    return {"message": "Service added successfully", "service_id": str(result.inserted_id)}


# Update service details (Admin only)
def update_service(service_id: str, name: Optional[str], description: Optional[str], price: Optional[float],
                   image: Optional[str]):
    update_data = {}
    if name:
        update_data["name"] = name
    if description:
        update_data["description"] = description
    if price is not None:
        update_data["price"] = price
    if image:
        update_data["image"] = image

    result = services_collection.update_one({"_id": ObjectId(service_id)}, {"$set": update_data})
    if result.matched_count:
        return {"message": "Service updated successfully"}
    return {"error": "Service not found"}


# Delete a service (Admin only)
def delete_service(service_id: str):
    result = services_collection.delete_one({"_id": ObjectId(service_id)})
    if result.deleted_count:
        return {"message": "Service deleted successfully"}
    return {"error": "Service not found"}
