from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from bson import ObjectId


# Booking Status
class BookingStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Booking Model
class Booking(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    provider_id: str
    service_id: str
    status: BookingStatus = BookingStatus.PENDING
    scheduled_date: datetime
    location: str
    additional_notes: Optional[str] = None
    payment_method: str
    paid: bool = False
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v)
        }



# Booking creation model
class BookingCreate(BaseModel):
    provider_id: str
    service_id: str
    scheduled_date: datetime
    location: str
    payment_method: str
    additional_notes: Optional[str] = None


# Booking update model
class BookingUpdate(BaseModel):
    status: BookingStatus
    scheduled_date: Optional[datetime] = None
    additional_notes: Optional[str] = None


# Service Model
class Service(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    image: Optional[str] = None  # Cloudinary URL
    created_at: datetime = datetime.utcnow()
