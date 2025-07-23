from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    PROVIDER = "provider"
    ADMIN = "admin"


class ProviderBase(BaseModel):
    user_id: str = Field(..., description="Reference to User ID")
    services_offered: List[str] = Field(
        default_factory=list,
        description="List of service IDs this provider offers"
    )
    bio: Optional[str] = None
    experience_years: Optional[int] = 0
    rating: float = 0.0
    base_price: float = 0.0
    address: Optional[str] = None
    skills: List[str] = []
    is_available: bool = True

class ProviderCreate(ProviderBase):
    pass


class ProviderResponse(ProviderBase):
    id: str = Field(..., alias="_id")
    created_at: datetime
    profile_image: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProviderUpdate(BaseModel):
    bio: Optional[str] = Field(None, example="Experienced plumber with 5+ years of service.")
    experience_years: Optional[int] = Field(None, example=5)
    base_price: Optional[float] = Field(None, example=2000.0)
    skills: Optional[List[str]] = Field(None, example=["Plumbing", "Pipe Installation", "Leak Repairs"])


class ToggleAvailability(BaseModel):
    is_available: bool = Field(..., example=True)


class ProviderApproval(BaseModel):
    provider_id: str = Field(..., example="65f123456789abcd12345678")

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None

class AvailabilityUpdate(BaseModel):
    is_available: bool


class DashboardStatsResponse(BaseModel):
    total_services: int
    total_bookings: int
    pending_bookings: int
    recent_earnings: float
    average_rating: float

class EarningsResponse(BaseModel):
    period: str
    total_earnings: float
    total_bookings: int
    start_date: str
    end_date: str

class BookingResponse(BaseModel):
    id: str
    service_id: Optional[str]
    user_id: str
    status: str
    price: float
    scheduled_date: datetime
    created_at: Optional[datetime]
    completed_at: Optional[datetime]

class ProviderProfileUpdate(BaseModel):
    bio: Optional[str]
    experience_years: Optional[int]
    base_price: Optional[float]
    skills: Optional[List[str]]
