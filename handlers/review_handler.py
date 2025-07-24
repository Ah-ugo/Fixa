from datetime import datetime
from bson import ObjectId
from db import reviews_collection, bookings_collection, providers_collection
from models.review import (
    ReviewFilter,
    ReviewSortField,
    SortOrder,
    PaginatedReviewResponse
)
from typing import Optional, Dict


def submit_review(booking_id: str, user_id: str, rating: float, comment: str = None):
    """Submit a review and update provider's average rating"""
    booking = bookings_collection.find_one({"_id": ObjectId(booking_id), "user_id": user_id})
    if not booking:
        return {"error": "Booking not found or you are not authorized to review this booking"}

    # Check if review already exists for this booking
    existing_review = reviews_collection.find_one({"booking_id": booking_id})
    if existing_review:
        return {"error": "You've already reviewed this booking"}

    provider_id = booking["provider_id"]
    review = {
        "user_id": user_id,
        "provider_id": provider_id,
        "booking_id": booking_id,
        "rating": rating,
        "comment": comment,
        "created_at": datetime.utcnow()
    }

    result = reviews_collection.insert_one(review)
    if result.inserted_id:
        update_provider_rating(provider_id)
        return {"message": "Review submitted successfully", "review_id": str(result.inserted_id)}
    return {"error": "Failed to submit review"}


def get_provider_reviews(
        provider_id: str,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "date",
        sort_order: str = "desc",
        filters: Optional[Dict] = None
) -> PaginatedReviewResponse:
    """Get paginated and filtered reviews for a provider"""
    query = {"provider_id": provider_id}

    # Apply filters
    if filters:
        if filters.get("min_rating"):
            query["rating"] = {"$gte": filters["min_rating"]}
        if filters.get("max_rating"):
            if "rating" in query:
                query["rating"]["$lte"] = filters["max_rating"]
            else:
                query["rating"] = {"$lte": filters["max_rating"]}
        if filters.get("star_rating"):
            query["rating"] = filters["star_rating"]

    # Calculate skip for pagination
    skip = (page - 1) * limit

    # Determine sort field and order
    sort_field = "created_at" if sort_by == "date" else "rating"
    sort_direction = -1 if sort_order == "desc" else 1

    # Get total count for pagination
    total = reviews_collection.count_documents(query)

    # Get paginated results
    reviews = list(
        reviews_collection.find(query)
        .sort(sort_field, sort_direction)
        .skip(skip)
        .limit(limit)
    )

    # Convert to response format
    reviews_list = [{
        "id": str(review["_id"]),
        "user_id": review["user_id"],
        "provider_id": review["provider_id"],
        "rating": review["rating"],
        "comment": review.get("comment"),
        "created_at": review["created_at"]
    } for review in reviews]

    return PaginatedReviewResponse(
        reviews=reviews_list,
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit
    )


def get_rating_stats(provider_id: str) -> Dict:
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
            "provider_id": provider_id,
            "average": 0,
            "count": 0,
            "breakdown": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }

    stats = result[0]
    return {
        "provider_id": provider_id,
        "average": stats["average"],
        "count": stats["count"],
        "breakdown": {
            1: stats["1_star"],
            2: stats["2_star"],
            3: stats["3_star"],
            4: stats["4_star"],
            5: stats["5_star"]
        }
    }


def update_provider_rating(provider_id: str):
    """Update provider's average rating based on all reviews"""
    stats = get_rating_stats(provider_id)
    providers_collection.update_one(
        {"_id": ObjectId(provider_id)},
        {"$set": {"rating": stats["average"]}}
    )

def delete_review(review_id: str, user_id: str):
    """Delete a review if the user is authorized"""
    review = reviews_collection.find_one({"_id": ObjectId(review_id), "user_id": user_id})
    if not review:
        return {"error": "Review not found or you are not authorized to delete this review"}

    result = reviews_collection.delete_one({"_id": ObjectId(review_id)})
    if result.deleted_count:
        update_provider_rating(review["provider_id"])
        return {"message": "Review deleted successfully"}
    return {"error": "Failed to delete review"}
