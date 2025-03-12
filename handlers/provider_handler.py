from db import providers_collection, users_collection
from typing import List, Optional
from bson import ObjectId


def get_approved_providers():
    return list(providers_collection.find({"is_approved": True}, {"password": 0}))


def get_provider_by_id(provider_id: str):
    return providers_collection.find_one({"_id": ObjectId(provider_id)}, {"password": 0})


def get_providers_by_service(service_id: str):
    return list(providers_collection.find({"services_offered": service_id, "is_approved": True}))


def toggle_provider_availability(provider_id: str, is_available: bool):
    return providers_collection.update_one({"_id": ObjectId(provider_id)}, {"$set": {"is_available": is_available}})


def update_provider_profile(provider_id: str, bio: Optional[str], experience_years: Optional[int],
                            base_price: Optional[float], skills: Optional[List[str]]):
    update_data = {}
    if bio is not None:
        update_data["bio"] = bio
    if experience_years is not None:
        update_data["experience_years"] = experience_years
    if base_price is not None:
        update_data["base_price"] = base_price
    if skills is not None:
        update_data["skills"] = skills

    return providers_collection.update_one({"_id": ObjectId(provider_id)}, {"$set": update_data})


def get_top_rated_providers():
    return list(providers_collection.find({"is_approved": True}).sort("rating", -1).limit(10))


def get_providers_nearby(user_location: str):
    return list(providers_collection.find({"address": {"$regex": user_location, "$options": "i"}, "is_approved": True}))


def approve_provider(provider_id: str):
    return providers_collection.update_one({"_id": ObjectId(provider_id)}, {"$set": {"is_approved": True}})


def delete_provider(provider_id: str):
    return providers_collection.delete_one({"_id": ObjectId(provider_id)})
