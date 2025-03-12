from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating should be between 1 and 5")
    comment: Optional[str] = Field(None, description="Optional comment about the provider")


class ReviewCreate(ReviewBase):
    booking_id: str = Field(..., description="ID of the booking being reviewed")


class ReviewResponse(ReviewBase):
    id: str
    user_id: str
    provider_id: str
    created_at: datetime

    class Config:
        orm_mode = True
