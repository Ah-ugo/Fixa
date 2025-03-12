from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Notification model
class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str

    class Config:
        schema_extra = {
            "example": {
                "user_id": "65f123456789abcd12345678",
                "title": "Service Update",
                "message": "Your booking has been confirmed."
            }
        }

# Message model
class MessageCreate(BaseModel):
    user_id: str
    provider_id: str
    sender_id: str
    message: str

    class Config:
        schema_extra = {
            "example": {
                "user_id": "65f123456789abcd12345678",
                "provider_id": "65f87654321abcdef9876543",
                "sender_id": "65f123456789abcd12345678",
                "message": "Hello, is the service still available?"
            }
        }

