from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum

class ReviewSortField(str, Enum):
    DATE = "date"
    RATING = "rating"

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


# class ReviewBase(BaseModel):
#     rating: float = Field(..., ge=1.0, le=5.0, description="Rating should be between 1 and 5")
#     comment: Optional[str] = Field(None, description="Optional comment about the provider")

class ReviewBase(BaseModel):
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating should be between 1 and 5")
    comment: Optional[str] = Field(None, description="Optional comment about the provider")

    @validator('rating')
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return round(v * 2) / 2

class ReviewCreate(ReviewBase):
    booking_id: str = Field(..., description="ID of the booking being reviewed")


class ReviewResponse(ReviewBase):
    id: str
    user_id: str
    provider_id: str
    created_at: datetime

    class Config:
        orm_mode = True



class ReviewFilter(BaseModel):
    min_rating: Optional[int] = Field(None, ge=1, le=5)
    max_rating: Optional[int] = Field(None, ge=1, le=5)
    star_rating: Optional[int] = Field(None, ge=1, le=5)


class ReviewQueryParams(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    sort_by: ReviewSortField = ReviewSortField.DATE
    sort_order: SortOrder = SortOrder.DESC
    filter: Optional[ReviewFilter] = None


class PaginatedReviewResponse(BaseModel):
    reviews: List[ReviewResponse]
    total: int
    page: int
    limit: int
    total_pages: int




class RatingStatsResponse(BaseModel):
    provider_id: str
    average: float
    count: int
    breakdown: Dict[int, int]

class AverageRatingResponse(BaseModel):
    provider_id: str
    average_rating: float
    total_reviews: int
