from pydantic import BaseModel, Field
from typing import Optional


class ServiceBase(BaseModel):
    name: str = Field(..., title="Service Name", min_length=2)
    description: Optional[str] = Field(None, title="Service Description")
    price: float = Field(..., title="Service Price", gt=0)
    image: Optional[str] = Field(None, title="Service Image URL")


class ServiceCreate(ServiceBase):
    """Model for creating a new service."""
    pass


class ServiceUpdate(BaseModel):
    """Model for updating service details."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None


class ServiceResponse(ServiceBase):
    """Model for returning service details."""
    id: str = Field(..., alias="_id")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
