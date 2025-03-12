from datetime import datetime
from bson import ObjectId
from db import reviews_collection, bookings_collection, providers_collection


# Submit a review & rating for a provider
def submit_review(booking_id: str, user_id: str, rating: float, comment: str = None):
    booking = bookings_collection.find_one({"_id": ObjectId(booking_id), "user_id": user_id})
    if not booking:
        return {"error": "Booking not found or you are not authorized to review this booking"}

    provider_id = booking["provider_id"]
    review = {
        "user_id": user_id,
        "provider_id": provider_id,
        "rating": rating,
        "comment": comment,
        "created_at": datetime.utcnow()
    }

    result = reviews_collection.insert_one(review)
    if result.inserted_id:
        update_provider_rating(provider_id)
        return {"message": "Review submitted successfully", "review_id": str(result.inserted_id)}
    return {"error": "Failed to submit review"}


# Get all reviews for a provider
def get_provider_reviews(provider_id: str):
    reviews = list(reviews_collection.find({"provider_id": provider_id}))
    for review in reviews:
        review["_id"] = str(review["_id"])
    return reviews


# Delete a review
def delete_review(review_id: str, user_id: str):
    review = reviews_collection.find_one({"_id": ObjectId(review_id), "user_id": user_id})
    if not review:
        return {"error": "Review not found or you are not authorized to delete this review"}

    result = reviews_collection.delete_one({"_id": ObjectId(review_id)})
    if result.deleted_count:
        update_provider_rating(review["provider_id"])
        return {"message": "Review deleted successfully"}
    return {"error": "Failed to delete review"}


# Helper function to update provider's average rating
def update_provider_rating(provider_id: str):
    reviews = list(reviews_collection.find({"provider_id": provider_id}))
    if not reviews:
        providers_collection.update_one({"_id": ObjectId(provider_id)}, {"$set": {"rating": 0.0}})
        return

    avg_rating = sum(review["rating"] for review in reviews) / len(reviews)
    providers_collection.update_one({"_id": ObjectId(provider_id)}, {"$set": {"rating": avg_rating}})
