from fastapi import APIRouter, HTTPException, Depends
from models.booking import BookingCreate, BookingUpdate, Booking, BookingStatus
from handlers.booking_handler import (
    create_booking,
    get_booking_by_id,
    get_user_bookings,
    get_provider_bookings,
    update_booking_status,
    cancel_booking,
    delete_booking,
)
from services.auth_service import get_current_user
from db import services_collection

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=Booking)
def create_new_booking(booking_data: BookingCreate, user: dict = Depends(get_current_user)):

    service = services_collection.find_one({"_id": ObjectId(booking_data.service_id)})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    booking = create_booking({
        **booking_data.dict(),
        "user_id": user["_id"],
        "service_id": str(service["_id"])  # Ensure service_id is properly converted
    })

    if not booking:
        raise HTTPException(status_code=400, detail="Booking could not be created")
    return booking

# Get booking details by ID (Authenticated users or providers)
@router.get("/{booking_id}", response_model=Booking)
def get_booking(booking_id: str, user: dict = Depends(get_current_user)):
    booking = get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if user["_id"] not in [booking["user_id"], booking["provider_id"]] and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return booking

@router.get("/all/user", response_model=list[Booking])
def get_user_all_bookings(user: dict = Depends(get_current_user)):
    return get_user_bookings(user["_id"])

# Get all bookings for a provider (Provider or admin only)
@router.get("/provider/{provider_id}", response_model=list[Booking])
def get_provider_all_bookings(provider_id: str, user: dict = Depends(get_current_user)):
    if user["_id"] != provider_id and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return get_provider_bookings(provider_id)

# Update booking status (Provider or admin only)
@router.put("/{booking_id}/status", response_model=Booking)
def update_status(booking_id: str, update_data: BookingUpdate, user: dict = Depends(get_current_user)):
    booking = get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if user["_id"] != booking["provider_id"] and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    updated_booking = update_booking_status(booking_id, update_data.status)
    if not updated_booking:
        raise HTTPException(status_code=400, detail="Could not update booking status")
    return updated_booking

# Cancel a booking (User, provider, or admin only)
@router.put("/{booking_id}/cancel", response_model=Booking)
def cancel_existing_booking(booking_id: str, user: dict = Depends(get_current_user)):
    booking = get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if user["_id"] not in [booking["user_id"], booking["provider_id"]] and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    cancelled_booking = cancel_booking(booking_id)
    if not cancelled_booking:
        raise HTTPException(status_code=400, detail="Could not cancel booking")
    return cancelled_booking

# Delete a booking (Admin only)
@router.delete("/{booking_id}", response_model=dict)
def remove_booking(booking_id: str, user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    if not delete_booking(booking_id):
        raise HTTPException(status_code=400, detail="Could not delete booking")
    return {"message": "Booking deleted successfully"}