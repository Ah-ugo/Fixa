from db import users_collection, providers_collection, bookings_collection, transactions_collection
from bson import ObjectId

def serialize_document(document):
    """Convert MongoDB document ObjectId to string."""
    document["_id"] = str(document["_id"])
    return document

def get_all_users():
    """Retrieve all users (Admin only)"""
    users = users_collection.find({}, {"password": 0})  # Exclude password field
    return [serialize_document(user) for user in users]

def get_all_providers():
    """Retrieve all service providers"""
    providers = providers_collection.find({}, {"password": 0})
    return [serialize_document(provider) for provider in providers]

def get_all_bookings():
    """Retrieve all bookings"""
    bookings = bookings_collection.find()
    return [serialize_document(booking) for booking in bookings]

def get_all_wallet_transactions():
    """Retrieve all wallet transactions"""
    transactions = transactions_collection.find()
    return [serialize_document(transaction) for transaction in transactions]


def approve_withdrawal(withdrawal_id: str):
    """Approve provider withdrawal request"""
    try:
        withdrawal_obj_id = ObjectId(withdrawal_id)
    except Exception:
        return {"error": "Invalid withdrawal ID format"}

    transaction = transactions_collection.find_one({"_id": withdrawal_obj_id})
    if not transaction:
        return {"error": "Transaction not found"}

    if transaction.get("status") != "pending":
        return {"error": "Transaction is not pending"}

    result = transactions_collection.update_one(
        {"_id": withdrawal_obj_id, "status": "pending"},
        {"$set": {"status": "approved"}}
    )
    return {"success": result.modified_count > 0}

def reject_withdrawal(withdrawal_id: str):
    """Reject provider withdrawal request"""
    result = transactions_collection.update_one(
        {"_id": ObjectId(withdrawal_id), "status": "pending"},
        {"$set": {"status": "rejected"}}
    )
    return result.modified_count > 0

def delete_user(user_id: str):
    """Delete a user (Admin only)"""
    result = users_collection.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0

def delete_provider(provider_id: str):
    """Delete a provider"""
    result = providers_collection.delete_one({"_id": ObjectId(provider_id)})
    return result.deleted_count > 0

def get_current_admin(admin_id: str):
    """Retrieve current admin details"""
    admin = users_collection.find_one({"_id": ObjectId(admin_id), "role": "admin"}, {"password": 0})
    if not admin:
        return {"error": "Admin not found"}
    return serialize_document(admin)
