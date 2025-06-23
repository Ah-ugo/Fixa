from fastapi import APIRouter, HTTPException, Depends
from handlers.wallet_handler import (
    generate_monnify_payment_link,
    confirm_wallet_funding,
    get_wallet_balance,
    get_provider_wallet_balance,
    request_withdrawal,
    approve_withdrawal,
    pay_for_service,
    mark_cash_on_delivery,
)
from models.user import User  # Assuming user model contains role-based access
from services.auth_service import get_current_user  # Function to get authenticated user

router = APIRouter()


# Generate Monnify payment link (Users)
@router.post("/fund")
def fund_wallet(amount: float, user: User = Depends(get_current_user)):
    print(user)
    return generate_monnify_payment_link(user["_id"], amount)


# Confirm wallet funding via webhook (Monnify)
@router.post("/confirm-funding")
def confirm_funding(reference: str):
    response = confirm_wallet_funding(reference)
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    return response


# Get user wallet balance
@router.get("/balance")
def wallet_balance(user: User = Depends(get_current_user)):
    return get_wallet_balance(user["_id"])


# Get provider wallet balance
@router.get("/provider-balance")
def provider_balance(provider_id: str, user: User = Depends(get_current_user)):
    if user.role != "admin" and user.id != provider_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return get_provider_wallet_balance(provider_id)


# Provider requests withdrawal
@router.post("/withdraw")
def withdraw_request(amount: float, user: User = Depends(get_current_user)):
    response = request_withdrawal(user.id, amount)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return response


# Admin approves withdrawal
@router.post("/approve-withdrawal")
def approve_withdrawal_request(withdrawal_id: str, user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admins only.")

    response = approve_withdrawal(withdrawal_id)
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    return response


# Pay for a service using wallet balance
@router.post("/pay-service/{booking_id}")
def pay_service(booking_id: str, user: User = Depends(get_current_user)):
    response = pay_for_service(booking_id)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return response


# Mark booking as paid via cash on delivery
@router.post("/cash-on-delivery/{booking_id}")
def mark_cod(booking_id: str, user: User = Depends(get_current_user)):
    response = mark_cash_on_delivery(booking_id)
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    return response
