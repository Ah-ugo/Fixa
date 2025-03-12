from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId
from db import reviews_collection
from models.review import ReviewCreate
from services.auth_service import get_current_user
from handlers.review_handler import (  # Importing functions
    submit_review,
    get_provider_reviews,
    delete_review
)

router = APIRouter()


@router.post("/", response_model=dict)
def create_review(data: ReviewCreate, user: dict = Depends(get_current_user)):
    """Submit a review & rating for a provider"""
    result = submit_review(data.booking_id, user["id"], data.rating, data.comment)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{provider_id}", response_model=List[dict])
def provider_reviews(provider_id: str):
    """Retrieve all reviews for a provider"""
    return get_provider_reviews(provider_id)


@router.delete("/{review_id}", response_model=dict)
def remove_review(review_id: str, user: dict = Depends(get_current_user)):
    """Delete a review if the user is authorized"""
    result = delete_review(review_id, user["id"])
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
