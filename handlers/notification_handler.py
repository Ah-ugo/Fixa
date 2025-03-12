from datetime import datetime
from db import users_collection, notifications_collection, messages_collection

# Send notification (Admin only)
def send_notification(user_id: str, title: str, message: str):
    notification = {
        "user_id": user_id,
        "title": title,
        "message": message,
        "created_at": datetime.utcnow(),
        "is_read": False
    }
    result = notifications_collection.insert_one(notification)
    return {"notification_id": str(result.inserted_id), "message": "Notification sent successfully"}

# Get all notifications for a user
def get_notifications(user_id: str):
    notifications = list(notifications_collection.find({"user_id": user_id}))
    for notification in notifications:
        notification["_id"] = str(notification["_id"])
    return notifications

# Send message (Chat between user & provider)
def send_message(user_id: str, provider_id: str, sender_id: str, message: str):
    chat_message = {
        "user_id": user_id,
        "provider_id": provider_id,
        "sender_id": sender_id,
        "message": message,
        "timestamp": datetime.utcnow()
    }
    result = messages_collection.insert_one(chat_message)
    return {"message_id": str(result.inserted_id), "message": "Message sent successfully"}

# Get messages between user and provider
def get_messages(user_id: str, provider_id: str):
    messages = list(messages_collection.find({
        "$or": [
            {"user_id": user_id, "provider_id": provider_id},
            {"user_id": provider_id, "provider_id": user_id}
        ]
    }))
    for message in messages:
        message["_id"] = str(message["_id"])
    return messages
