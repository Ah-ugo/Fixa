from pydantic import BaseModel, Field
from typing import List, Optional


class ProviderUpdate(BaseModel):
    bio: Optional[str] = Field(None, example="Experienced plumber with 5+ years of service.")
    experience_years: Optional[int] = Field(None, example=5)
    base_price: Optional[float] = Field(None, example=2000.0)
    skills: Optional[List[str]] = Field(None, example=["Plumbing", "Pipe Installation", "Leak Repairs"])


class ToggleAvailability(BaseModel):
    is_available: bool = Field(..., example=True)


class ProviderApproval(BaseModel):
    provider_id: str = Field(..., example="65f123456789abcd12345678")
