from db import services_collection
from bson import ObjectId
from typing import Optional
from services.cloudinary_service import upload_image
from fastapi import UploadFile


# Get list of available services
def get_services():
    services = list(services_collection.find({}, {"_id": 0}))
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
