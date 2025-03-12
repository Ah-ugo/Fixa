from pydantic import BaseModel, EmailStr, Field, constr
from typing import List, Optional
from datetime import datetime
from enum import Enum


# User Roles
class UserRole(str, Enum):
    USER = "user"
    PROVIDER = "provider"
    ADMIN = "admin"

# User Model
class User(BaseModel):
    id: str
    full_name: str = Field(..., min_length=3)
    email: str
    phone: str
    role: UserRole = UserRole.USER
    password: str
    profile_image: Optional[str] = None  # Cloudinary URL
    created_at: datetime = datetime.utcnow()


# Admin Model
class Admin(BaseModel):
    id: str
    full_name: str
    email: str
    password: str
    profile_image: Optional[str] = None  # Cloudinary URL
    created_at: datetime = datetime.utcnow()


# Provider Model (Service Provider)
class Provider(BaseModel):
    id: str
    user_id: str  # References User ID
    profile_image: Optional[str] = None  # Cloudinary URL
    services_offered: List[str]
    bio: Optional[str] = None
    experience_years: Optional[int] = 0
    rating: float = 0.0
    base_price: float = 0.0
    tasks_completed: int = 0
    address: Optional[str] = None
    skills: List[str] = []
    is_available: bool = True
    created_at: datetime = datetime.utcnow()


# Review Model
class Review(BaseModel):
    id: str
    user_id: str  # References User ID
    provider_id: str  # References Provider ID
    rating: float = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    created_at: datetime = datetime.utcnow()


# Support Ticket Model
class SupportTicket(BaseModel):
    id: str
    user_id: str
    subject: str
    message: str
    status: str = "open"
    created_at: datetime = datetime.utcnow()

class UserLoginSchema(BaseModel):
    email: str
    password: str

# Token Response Schema
class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

# User Registration Model
class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=50)
    email: str
    password: constr(min_length=6, max_length=100)
    role: Optional[str] = Field(default="user", pattern="^(user|provider)$")

    # role: Optional[str] = Field("user", regex="^(user|provider)$")  # Default role is 'user'
    phone_number: Optional[str] = Field(None, pattern="^\+?\d{10,15}$")  # Optional phone number
    address: Optional[str] = Field(None, max_length=200)
    profile_image: Optional[str] = None  # URL to profile image

# User Login Model
class UserLogin(BaseModel):
    email: str
    password: str

# Update Profile Model
class UpdateProfile(BaseModel):
    full_name: Optional[str] = Field(None, min_length=3, max_length=50)
    phone_number: Optional[str] = Field(None, pattern="^\+?\d{10,15}$")
    address: Optional[str] = Field(None, max_length=200)
    profile_image: Optional[str] = None

# Reset Password Model
class ResetPassword(BaseModel):
    email: str
    new_password: constr(min_length=6, max_length=100)
