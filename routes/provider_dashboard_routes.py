from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from datetime import datetime, timedelta
from typing import List, Optional
from bson import ObjectId
from models.provider import (
    DashboardStatsResponse,
    EarningsResponse,
    BookingResponse,
    ServiceUpdate,
    AvailabilityUpdate
)
from services.auth_service import get_current_provider
from db import (
    users_collection,
    services_collection,
    bookings_collection,
    transactions_collection,
    reviews_collection
)
import tempfile
import os
from services.cloudinary_service import upload_image

router = APIRouter()


# --------------------------
# Dashboard Statistics
# --------------------------

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
        current_provider: dict = Depends(get_current_provider)
):
    """
    Get provider dashboard statistics including:
    - Total services offered
    - Total bookings
    - Pending bookings
    - Recent earnings
    - Average rating
    """
    provider_id = current_provider["_id"]

    try:
        # Total services offered
        total_services = len(current_provider.get("services_offered", []))

        # Total bookings
        total_bookings = bookings_collection.count_documents({
            "provider_id": str(provider_id)
        })

        # Pending bookings
        pending_bookings = bookings_collection.count_documents({
            "provider_id": str(provider_id),
            "status": "pending"
        })

        # Recent earnings (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        earnings_result = bookings_collection.aggregate([
            {
                "$match": {
                    "provider_id": str(provider_id),
                    "status": "completed",
                    "completed_at": {"$gte": thirty_days_ago}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$price"}
                }
            }
        ])
        earnings = list(earnings_result)
        recent_earnings = earnings[0]["total"] if earnings else 0

        # Average rating
        avg_rating = current_provider.get("rating", 0)

        return {
            "total_services": total_services,
            "total_bookings": total_bookings,
            "pending_bookings": pending_bookings,
            "recent_earnings": recent_earnings,
            "average_rating": avg_rating
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------
# Earnings Management
# --------------------------

@router.get("/earnings", response_model=EarningsResponse)
async def get_earnings(
        period: str = Query("month", description="Time period: week, month, or year"),
        current_provider: dict = Depends(get_current_provider)
):
    """
    Get provider earnings for a specific time period
    """
    provider_id = current_provider["_id"]

    try:
        # Calculate date range
        now = datetime.now()
        if period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "year":
            start_date = now - timedelta(days=365)
        else:
            raise HTTPException(status_code=400, detail="Invalid period specified")

        # Get earnings data
        pipeline = [
            {
                "$match": {
                    "provider_id": str(provider_id),
                    "status": "completed",
                    "completed_at": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_earnings": {"$sum": "$price"},
                    "total_bookings": {"$sum": 1}
                }
            }
        ]

        result = list(bookings_collection.aggregate(pipeline))

        if not result:
            return {
                "period": period,
                "total_earnings": 0,
                "total_bookings": 0,
                "start_date": start_date.isoformat(),
                "end_date": now.isoformat()
            }

        return {
            "period": period,
            "total_earnings": result[0]["total_earnings"],
            "total_bookings": result[0]["total_bookings"],
            "start_date": start_date.isoformat(),
            "end_date": now.isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------
# Booking Management
# --------------------------

@router.get("/bookings", response_model=List[BookingResponse])
async def get_provider_bookings(
        status: Optional[str] = Query(None, description="Filter by booking status"),
        limit: int = Query(10, description="Number of bookings to return"),
        current_provider: dict = Depends(get_current_provider)
):
    """
    Get provider's bookings with optional status filtering
    """
    provider_id = current_provider["_id"]

    try:
        query = {"provider_id": str(provider_id)}
        if status:
            query["status"] = status

        bookings = list(bookings_collection.find(query)
                        .sort("scheduled_date", -1)
                        .limit(limit))

        return [{
            "id": str(booking["_id"]),
            "service_id": booking.get("service_id"),
            "user_id": booking["user_id"],
            "status": booking["status"],
            "price": booking["price"],
            "scheduled_date": booking["scheduled_date"],
            "created_at": booking.get("created_at"),
            "completed_at": booking.get("completed_at")
        } for booking in bookings]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/bookings/{booking_id}/accept")
async def accept_booking(
        booking_id: str,
        current_provider: dict = Depends(get_current_provider)
):
    """
    Accept a booking request
    """
    try:
        result = bookings_collection.update_one(
            {
                "_id": ObjectId(booking_id),
                "provider_id": str(current_provider["_id"]),
                "status": "pending"
            },
            {"$set": {"status": "accepted"}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Booking not found or already processed")

        return {"message": "Booking accepted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/bookings/{booking_id}/complete")
async def complete_booking(
        booking_id: str,
        current_provider: dict = Depends(get_current_provider)
):
    """
    Mark a booking as completed
    """
    try:
        result = bookings_collection.update_one(
            {
                "_id": ObjectId(booking_id),
                "provider_id": str(current_provider["_id"]),
                "status": "accepted"
            },
            {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.now()
                }
            }
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Booking not found or not in accepted state")

        return {"message": "Booking marked as completed"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------
# Profile Management
# --------------------------

@router.put("/profile")
async def update_provider_profile(
        bio: Optional[str] = None,
        experience_years: Optional[int] = None,
        base_price: Optional[float] = None,
        skills: Optional[List[str]] = None,
        current_provider: dict = Depends(get_current_provider)
):
    """
    Update provider profile information
    """
    provider_id = current_provider["_id"]

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
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        result = users_collection.update_one(
            {"_id": ObjectId(provider_id)},
            {"$set": update_data}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No changes made")

        return {"message": "Profile updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profile/image")
async def update_profile_image(
        image: UploadFile = File(...),
        current_provider: dict = Depends(get_current_provider)
):
    """
    Update provider profile image
    """
    provider_id = current_provider["_id"]

    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(await image.read())
            temp_path = temp_file.name

        # Upload to Cloudinary
        image_url = upload_image(temp_path, folder="provider_profiles")

        # Clean up temporary file
        os.unlink(temp_path)

        if isinstance(image_url, dict) and "error" in image_url:
            raise HTTPException(status_code=400, detail=image_url["error"])

        # Update provider record
        result = users_collection.update_one(
            {"_id": ObjectId(provider_id)},
            {"$set": {"profile_image": image_url}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Failed to update profile image")

        return {"message": "Profile image updated successfully", "image_url": image_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------
# Availability Management
# --------------------------

@router.put("/availability")
async def update_availability(
        is_available: bool,
        current_provider: dict = Depends(get_current_provider)
):
    """
    Update provider availability status
    """
    provider_id = current_provider["_id"]

    try:
        result = users_collection.update_one(
            {"_id": ObjectId(provider_id)},
            {"$set": {"is_available": is_available}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No changes made")

        return {"message": "Availability updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------
# Service Management
# --------------------------

@router.get("/services", response_model=List[dict])
async def get_my_services(
        current_provider: dict = Depends(get_current_provider)
):
    """
    Get all services offered by the current provider
    """
    provider_id = current_provider["_id"]

    try:
        provider = users_collection.find_one(
            {"_id": ObjectId(provider_id)},
            {"services_offered": 1}
        )

        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")

        service_ids = [ObjectId(id) for id in provider.get("services_offered", [])]
        services = list(services_collection.find({"_id": {"$in": service_ids}}))

        return [{
            "id": str(service["_id"]),
            "name": service["name"],
            "description": service["description"],
            "price": service["price"],
            "image": service.get("image")
        } for service in services]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/services/{service_id}")
async def add_my_service(
        service_id: str,
        current_provider: dict = Depends(get_current_provider)
):
    """
    Add a service to provider's offerings
    """
    provider_id = current_provider["_id"]

    try:
        # Verify service exists
        service = services_collection.find_one({"_id": ObjectId(service_id)})
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        # Add to provider's services
        result = users_collection.update_one(
            {"_id": ObjectId(provider_id)},
            {"$addToSet": {"services_offered": service_id}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Service already added")

        return {"message": "Service added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/services/{service_id}")
async def remove_my_service(
        service_id: str,
        current_provider: dict = Depends(get_current_provider)
):
    """
    Remove a service from provider's offerings
    """
    provider_id = current_provider["_id"]

    try:
        result = users_collection.update_one(
            {"_id": ObjectId(provider_id)},
            {"$pull": {"services_offered": service_id}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Service not found in profile")

        return {"message": "Service removed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------
# Reviews and Ratings
# --------------------------

@router.get("/reviews", response_model=List[dict])
async def get_my_reviews(
        current_provider: dict = Depends(get_current_provider)
):
    """
    Get all reviews for the current provider
    """
    provider_id = current_provider["_id"]

    try:
        reviews = list(reviews_collection.find({"provider_id": str(provider_id)})
                       .sort("created_at", -1))

        return [{
            "id": str(review["_id"]),
            "user_id": review["user_id"],
            "rating": review["rating"],
            "comment": review.get("comment"),
            "created_at": review["created_at"]
        } for review in reviews]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))