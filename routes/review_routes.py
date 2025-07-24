from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from bson import ObjectId
from db import reviews_collection
from models.review import (
    ReviewCreate,
    ReviewResponse,
    ReviewFilter,
    ReviewQueryParams,
    PaginatedReviewResponse,
    RatingStatsResponse,
    AverageRatingResponse,
    ReviewSortField,
    SortOrder
)
from services.auth_service import get_current_user
from handlers.review_handler import (
    submit_review,
    get_provider_reviews,
    delete_review, get_rating_stats
)

router = APIRouter()


@router.post("/", response_model=dict)
def create_review(data: ReviewCreate, user: dict = Depends(get_current_user)):
    """Submit a review & rating for a provider"""
    result = submit_review(data.booking_id, user["_id"], data.rating, data.comment)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{provider_id}", response_model=PaginatedReviewResponse)
def provider_reviews(
        provider_id: str,
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        sort_by: ReviewSortField = Query(ReviewSortField.DATE),
        sort_order: SortOrder = Query(SortOrder.DESC),
        min_rating: Optional[int] = Query(None, ge=1, le=5),
        max_rating: Optional[int] = Query(None, ge=1, le=5),
        star_rating: Optional[int] = Query(None, ge=1, le=5)
):
    """Retrieve paginated and filtered reviews for a provider"""
    filters = {}
    if min_rating is not None:
        filters["min_rating"] = min_rating
    if max_rating is not None:
        filters["max_rating"] = max_rating
    if star_rating is not None:
        filters["star_rating"] = star_rating

    return get_provider_reviews(
        provider_id,
        page=page,
        limit=limit,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
        filters=filters if filters else None
    )


@router.delete("/{review_id}", response_model=dict)
def remove_review(review_id: str, user: dict = Depends(get_current_user)):
    """Delete a review if the user is authorized"""
    result = delete_review(review_id, user["_id"])
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{provider_id}/average", response_model=AverageRatingResponse)
def get_provider_average_rating(provider_id: str):
    """Get a provider's average rating"""
    stats = get_rating_stats(provider_id)
    return {
        "provider_id": provider_id,
        "average_rating": stats["average"],
        "total_reviews": stats["count"]
    }



@router.get("/{provider_id}/stats", response_model=RatingStatsResponse)
def get_provider_rating_stats(provider_id: str):
    """Get detailed rating statistics for a provider"""
    return get_rating_stats(provider_id)