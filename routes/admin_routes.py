from fastapi import APIRouter, Depends, HTTPException
from db import users_collection, providers_collection, bookings_collection, transactions_collection
from bson import ObjectId
from models.user import User
from services.auth_service import get_current_admin
from handlers.admin_handler import get_all_users as get_users, get_all_providers as get_providers, get_all_bookings as get_bookings, get_all_wallet_transactions as get_wallet_transactions, approve_withdrawal as withdrawal_approve, reject_withdrawal as withdrawal_rejection, delete_user as delete_user_data, delete_provider as delete_provider_data

router = APIRouter()

@router.get("/users", response_model=list)
def get_all_users(admin: User = Depends(get_current_admin)):
    """Retrieve all users (Admin only)"""
    return get_users()

@router.get("/providers", response_model=list)
def get_all_providers():
    """Retrieve all service providers"""
    return get_providers()

@router.get("/bookings", response_model=list)
def get_all_bookings():
    """Retrieve all bookings"""
    return get_bookings()

@router.get("/transactions", response_model=list)
def get_all_wallet_transactions():
    """Retrieve all wallet transactions"""
    return get_wallet_transactions()

@router.put("/withdrawals/{withdrawal_id}/approve")
def approve_withdrawal(withdrawal_id: str, admin: User = Depends(get_current_admin)):
    """Approve provider withdrawal request"""
    return withdrawal_approve(withdrawal_id)

@router.put("/withdrawals/{withdrawal_id}/reject")
def reject_withdrawal(withdrawal_id: str, admin: User = Depends(get_current_admin)):
    """Reject provider withdrawal request"""
    return withdrawal_rejection(withdrawal_id)

@router.delete("/users/{user_id}")
def delete_user(user_id: str, admin: User = Depends(get_current_admin)):
    """Delete a user (Admin only)"""
    return delete_user_data(user_id)

@router.delete("/providers/{provider_id}")
def delete_provider(provider_id: str, admin: User = Depends(get_current_admin)):
    """Delete a provider"""
    return delete_provider_data(provider_id)
