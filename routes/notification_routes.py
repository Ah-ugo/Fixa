from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from db import users_collection, notifications_collection, messages_collection
from models.notimess import NotificationCreate, MessageCreate
# from models.message import MessageCreate
from bson import ObjectId
# from handlers.auth_handler import get_current_user
# from handlers.admin_handler import get_current_admin
from services.auth_service import get_current_user, get_current_admin

router = APIRouter()

# Send notification (Admin only)
@router.post("/send", response_model=dict)
def send_notification(notification: NotificationCreate, admin: dict = Depends(get_current_admin)):
    notification_data = {
        "user_id": notification.user_id,
        "title": notification.title,
        "message": notification.message,
        "created_at": datetime.utcnow(),
        "is_read": False
    }
    result = notifications_collection.insert_one(notification_data)
    return {"notification_id": str(result.inserted_id), "message": "Notification sent successfully"}

# Get all notifications for a user
@router.get("/{user_id}", response_model=list)
def get_notifications(user_id: str, user: dict = Depends(get_current_user)):
    notifications = list(notifications_collection.find({"user_id": user_id}))
    for notification in notifications:
        notification["_id"] = str(notification["_id"])
    return notifications

# Send message (Chat between user & provider)
@router.post("/messages/send", response_model=dict)
def send_message(message: MessageCreate, user: dict = Depends(get_current_user)):
    chat_message = {
        "user_id": message.user_id,
        "provider_id": message.provider_id,
        "sender_id": message.sender_id,
        "message": message.message,
        "timestamp": datetime.utcnow()
    }
    result = messages_collection.insert_one(chat_message)
    return {"message_id": str(result.inserted_id), "message": "Message sent successfully"}

# Get messages between user and provider
@router.get("/messages/{user_id}/{provider_id}", response_model=list)
def get_messages(user_id: str, provider_id: str, user: dict = Depends(get_current_user)):
    messages = list(messages_collection.find({
        "$or": [
            {"user_id": user_id, "provider_id": provider_id},
            {"user_id": provider_id, "provider_id": user_id}
        ]
    }))
    for message in messages:
        message["_id"] = str(message["_id"])
    return messages
