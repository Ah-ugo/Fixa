from datetime import datetime
from typing import Optional
from db import bookings_collection, services_collection
from models.booking import BookingStatus
from bson import ObjectId

# Create a new booking
def create_booking(booking_data: dict) -> Optional[dict]:
    # Get the service to get the price
    service = services_collection.find_one({"_id": ObjectId(booking_data["service_id"])})
    if not service:
        return None

    # Add the service price to the booking
    booking_data["price"] = service["price"]
    booking_data["status"] = BookingStatus.PENDING.value
    booking_data["created_at"] = datetime.utcnow()
    booking_data["paid"] = False

    result = bookings_collection.insert_one(booking_data)
    if result.inserted_id:
        booking_data["_id"] = str(result.inserted_id)
        return booking_data
    return None

# Get booking details by ID
def get_booking_by_id(booking_id: str) -> Optional[dict]:
    try:
        booking = bookings_collection.find_one({"_id": ObjectId(booking_id)})
        if booking:
            booking["_id"] = str(booking["_id"])
            return booking
        return None
    except Exception:
        return None

# Get all bookings for a user
def get_user_bookings(user_id: str) -> list:
    bookings = bookings_collection.find({"user_id": user_id})
    return [{**b, "_id": str(b["_id"])} for b in bookings]

# Get all bookings for a provider
def get_provider_bookings(provider_id: str) -> list:
    bookings = bookings_collection.find({"provider_id": provider_id})
    return [{**b, "_id": str(b["_id"])} for b in bookings]

# Update booking status
def update_booking_status(booking_id: str, status: BookingStatus) -> Optional[dict]:
    try:
        result = bookings_collection.update_one(
            {"_id": ObjectId(booking_id)},
            {"$set": {"status": status.value}}
        )
        if result.modified_count:
            return get_booking_by_id(booking_id)
        return None
    except Exception:
        return None

# Cancel a booking
def cancel_booking(booking_id: str) -> Optional[dict]:
    return update_booking_status(booking_id, BookingStatus.CANCELLED)

# Delete a booking
def delete_booking(booking_id: str) -> bool:
    try:
        result = bookings_collection.delete_one({"_id": ObjectId(booking_id)})
        return result.deleted_count > 0
    except Exception:
        return False