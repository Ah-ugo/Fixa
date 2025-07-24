from fastapi import APIRouter, HTTPException, Depends, Query
from handlers.wallet_handler import (
    generate_monnify_payment_link,
    confirm_wallet_funding,
    get_wallet_balance,
    get_provider_wallet_balance,
    request_withdrawal,
    approve_withdrawal,
    pay_for_service,
    mark_cash_on_delivery,
get_recent_transactions,
    get_transaction_history,
    get_transaction_details
)
from services.auth_service import get_current_user
from models.wallet import WalletTransactionResponse
from typing import Optional
from datetime import datetime

router = APIRouter()


# Generate Monnify payment link (Users)
@router.post("/fund")
def fund_wallet(amount: float, user: dict = Depends(get_current_user)):
    return generate_monnify_payment_link(str(user["_id"]), amount)


# Confirm wallet funding via webhook (Monnify)
@router.post("/confirm-funding")
def confirm_funding(reference: str):
    response = confirm_wallet_funding(reference)
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    return response


# Get user wallet balance
@router.get("/balance")
def wallet_balance(user: dict = Depends(get_current_user)):
    return get_wallet_balance(str(user["_id"]))


# Get provider wallet balance
@router.get("/provider-balance")
def provider_balance(provider_id: str, user: dict = Depends(get_current_user)):
    # Convert both IDs to string for comparison
    user_id = str(user["_id"])
    provider_id = str(provider_id)

    if user.get("role") != "admin" and user_id != provider_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return get_provider_wallet_balance(provider_id)


# Provider requests withdrawal
@router.post("/withdraw")
def withdraw_request(amount: float, user: dict = Depends(get_current_user)):
    response = request_withdrawal(str(user["_id"]), amount)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return response


@router.get("/recent", response_model=list)
async def get_user_recent_transactions(
    limit: int = Query(5, description="Number of recent transactions to fetch"),
    user: dict = Depends(get_current_user)
):
    """Get user's recent transactions"""
    try:
        return get_recent_transactions(str(user["_id"]), limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history", response_model=WalletTransactionResponse)
async def get_user_transaction_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    user: dict = Depends(get_current_user)
):
    """Get paginated transaction history with filters"""
    try:
        return get_transaction_history(
            user_id=str(user["_id"]),
            page=page,
            limit=limit,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{transaction_id}", response_model=dict)
async def get_transaction_detail(
        transaction_id: str,
        user: dict = Depends(get_current_user)
):
    """Get details of a specific transaction"""
    try:
        transaction = get_transaction_details(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Verify the transaction belongs to the user
        if transaction["user_id"] != str(user["_id"]):
            raise HTTPException(status_code=403, detail="Access denied")

        return transaction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Admin approves withdrawal
@router.post("/approve-withdrawal")
def approve_withdrawal_request(withdrawal_id: str, user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admins only.")

    response = approve_withdrawal(withdrawal_id)
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    return response


# Pay for a service using wallet balance
@router.post("/pay-service/{booking_id}")
def pay_service(booking_id: str, user: dict = Depends(get_current_user)):
    response = pay_for_service(booking_id)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return response


# Mark booking as paid via cash on delivery
@router.post("/cash-on-delivery/{booking_id}")
def mark_cod(booking_id: str, user: dict = Depends(get_current_user)):
    response = mark_cash_on_delivery(booking_id)
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    return response