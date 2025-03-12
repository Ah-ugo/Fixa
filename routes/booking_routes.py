from fastapi import APIRouter, HTTPException, Depends
# from models.booking import BookingStatus
from handlers.booking_handler import (
    create_booking,
    get_booking_by_id,
    get_user_bookings,
    get_provider_bookings,
    update_booking_status,
    cancel_booking,
    delete_booking,
)
from models.booking import BookingCreate, BookingUpdate, BookingStatus
from services.auth_service import get_current_user

router = APIRouter(prefix="/bookings", tags=["Bookings"])

# Create a new booking
@router.post("/", response_model=dict)
def create_new_booking(booking_data: BookingCreate, user: dict = Depends(get_current_user)):
    booking = create_booking(booking_data.dict())
    if not booking:
        raise HTTPException(status_code=400, detail="Booking could not be created")
    return booking

# Get booking details by ID
@router.get("/{booking_id}", response_model=dict)
def get_booking(booking_id: str):
    booking = get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

# Get all bookings for a user
@router.get("/user/{user_id}", response_model=list)
def get_user_all_bookings(user_id: str):
    return get_user_bookings(user_id)

# Get all bookings for a provider
@router.get("/provider/{provider_id}", response_model=list)
def get_provider_all_bookings(provider_id: str):
    return get_provider_bookings(provider_id)

# Update booking status
@router.put("/{booking_id}/status", response_model=dict)
def update_status(booking_id: str, update_data: BookingUpdate):
    updated_booking = update_booking_status(booking_id, update_data.status)
    if not updated_booking:
        raise HTTPException(status_code=400, detail="Could not update booking status")
    return updated_booking

# Cancel a booking
@router.put("/{booking_id}/cancel", response_model=dict)
def cancel_existing_booking(booking_id: str):
    cancelled_booking = cancel_booking(booking_id)
    if not cancelled_booking:
        raise HTTPException(status_code=400, detail="Could not cancel booking")
    return cancelled_booking

# Delete a booking
@router.delete("/{booking_id}")
def remove_booking(booking_id: str):
    if not delete_booking(booking_id):
        raise HTTPException(status_code=400, detail="Could not delete booking")
    return {"message": "Booking deleted successfully"}
