from datetime import datetime
from typing import Optional
from db import bookings_collection
from models.booking import BookingStatus
from bson import ObjectId

# Create a new booking
def create_booking(booking_data: dict) -> Optional[dict]:
    booking_data["created_at"] = datetime.utcnow()
    result = bookings_collection.insert_one(booking_data)
    if result.inserted_id:
        booking_data["_id"] = str(result.inserted_id)  # Convert ObjectId to string
        return booking_data  # Return dictionary with string ID
    return None



# Get booking details by ID
def get_booking_by_id(booking_id: str) -> Optional[dict]:
    booking = bookings_collection.find_one({"_id": ObjectId(booking_id)})
    if booking:
        booking["id"] = str(booking["_id"])
        del booking["_id"]
        return booking
    return None

# Get all bookings for a user
def get_user_bookings(user_id: str):
    bookings = bookings_collection.find({"user_id": user_id})
    return [{"id": str(b["_id"], **b)} for b in bookings]

# Get all bookings for a provider
def get_provider_bookings(provider_id: str):
    bookings = bookings_collection.find({"provider_id": provider_id})
    return [{"id": str(b["_id"], **b)} for b in bookings]

# Update booking status
def update_booking_status(booking_id: str, status: BookingStatus) -> Optional[dict]:
    result = bookings_collection.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"status": status.value}}
    )
    if result.modified_count:
        return get_booking_by_id(booking_id)
    return None

# Cancel a booking
def cancel_booking(booking_id: str) -> Optional[dict]:
    return update_booking_status(booking_id, BookingStatus.CANCELLED)

# Delete a booking
def delete_booking(booking_id: str) -> bool:
    result = bookings_collection.delete_one({"_id": ObjectId(booking_id)})
    return result.deleted_count > 0
