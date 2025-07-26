from datetime import datetime
from typing import Optional, List
from db import wallets_collection, transactions_collection, bookings_collection, services_collection
from bson.objectid import ObjectId
from models.wallet import (
    TransactionType,
    TransactionStatus,
    WalletTransaction,
    WalletTransactionResponse
)


# def serialize_transaction(transaction) -> dict:
#     if transaction and '_id' in transaction:
#         transaction['id'] = str(transaction['_id'])
#         transaction.pop('_id')
#     return transaction

def serialize_transaction(transaction) -> dict:
    """Properly serialize a transaction document from MongoDB"""
    if not transaction:
        return None

    # Set default status if missing
    status = transaction.get("status", TransactionStatus.COMPLETED)

    serialized = {
        "id": str(transaction["_id"]),
        "user_id": transaction.get("user_id"),
        "amount": transaction.get("amount", 0.0),
        "transaction_type": transaction.get("transaction_type"),
        "status": status,  # Use the status we determined
        "reference": transaction.get("reference", ""),
        "description": transaction.get("description"),
        "metadata": transaction.get("metadata"),
        "created_at": transaction.get("created_at", datetime.utcnow())
    }
    return {k: v for k, v in serialized.items() if v is not None}

# Generate Monnify payment link for funding wallet
def generate_monnify_payment_link(user_id: str, amount: float):
    payment_reference = f"MONNIFY_{user_id}_{int(datetime.utcnow().timestamp())}"
    transaction = {
        "user_id": user_id,
        "amount": amount,
        "transaction_type": "deposit",
        "reference": payment_reference,
        "created_at": datetime.utcnow()
    }
    transactions_collection.insert_one(transaction)
    return {"payment_link": f"https://monnify.com/pay/{payment_reference}", "reference": payment_reference}


# Monnify webhook to confirm wallet funding
def confirm_wallet_funding(reference: str):
    transaction = transactions_collection.find_one({"reference": reference})
    if not transaction:
        return {"error": "Transaction not found"}

    wallets_collection.update_one(
        {"user_id": transaction["user_id"]},
        {"$inc": {"balance": transaction["amount"]}},
        upsert=True
    )
    return {"message": "Wallet funded successfully"}


# Get user wallet balance
def get_wallet_balance(user_id: str):
    wallet = wallets_collection.find_one({"user_id": user_id})
    return {"balance": wallet["balance"] if wallet else 0.0}


# Get provider wallet balance
def get_provider_wallet_balance(provider_id: str):
    wallet = wallets_collection.find_one({"user_id": provider_id})
    return {"balance": wallet["balance"] if wallet else 0.0}


# Provider requests withdrawal
def request_withdrawal(provider_id: str, amount: float):
    wallet = wallets_collection.find_one({"user_id": provider_id})
    if not wallet or wallet["balance"] < amount:
        return {"error": "Insufficient balance"}

    withdrawal_request = {
        "user_id": provider_id,
        "amount": amount,
        "transaction_type": "withdrawal",
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    transactions_collection.insert_one(withdrawal_request)
    return {"message": "Withdrawal request submitted"}


# Admin approves withdrawal
def approve_withdrawal(withdrawal_id: str):
    withdrawal = transactions_collection.find_one(
        {"_id": ObjectId(withdrawal_id), "transaction_type": "withdrawal", "status": "pending"})
    if not withdrawal:
        return {"error": "Withdrawal request not found or already processed"}

    wallets_collection.update_one(
        {"user_id": withdrawal["user_id"]},
        {"$inc": {"balance": -withdrawal["amount"]}}
    )
    transactions_collection.update_one(
        {"_id": ObjectId(withdrawal_id)},
        {"$set": {"status": "approved"}}
    )
    return {"message": "Withdrawal approved"}


def get_recent_transactions(user_id: str, limit: int = 5) -> List[WalletTransaction]:
    """Get recent transactions for a user"""
    try:
        transactions = transactions_collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit)

        return [serialize_transaction(t) for t in transactions]
    except Exception as e:
        raise Exception(f"Error fetching transactions: {str(e)}")


def get_transaction_history(
        user_id: str,
        page: int = 1,
        limit: int = 10,
        transaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
) -> WalletTransactionResponse:
    """Get paginated transaction history with filters"""
    try:
        query = {"user_id": user_id}

        # Apply filters
        if transaction_type:
            query["transaction_type"] = transaction_type
        if start_date and end_date:
            query["created_at"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["created_at"] = {"$gte": start_date}
        elif end_date:
            query["created_at"] = {"$lte": end_date}

        # Get total count
        total = transactions_collection.count_documents(query)

        # Get paginated results
        transactions = transactions_collection.find(query).sort("created_at", -1).skip((page - 1) * limit).limit(limit)

        # Properly serialize each transaction
        serialized_transactions = [serialize_transaction(t) for t in transactions if t]

        return WalletTransactionResponse(
            transactions=serialized_transactions,
            total=total,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise Exception(f"Error fetching transaction history: {str(e)}")


def get_transaction_details(transaction_id: str) -> Optional[WalletTransaction]:
    """Get details of a specific transaction"""
    try:
        transaction = transactions_collection.find_one({"_id": ObjectId(transaction_id)})
        return serialize_transaction(transaction) if transaction else None
    except Exception as e:
        raise Exception(f"Error fetching transaction details: {str(e)}")


def pay_for_service(booking_id: str):
    # Get the booking
    booking = bookings_collection.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        return {"error": "Booking not found"}

    # Get the associated service to get the price
    service = services_collection.find_one({"_id": ObjectId(booking["service_id"])})
    if not service:
        return {"error": "Service not found"}

    price = service["price"]

    # Check wallet balance
    wallet = wallets_collection.find_one({"user_id": booking["user_id"]})
    if not wallet or wallet["balance"] < price:
        return {"error": "Insufficient wallet balance"}

    # Process payment
    wallets_collection.update_one(
        {"user_id": booking["user_id"]},
        {"$inc": {"balance": -price}}
    )

    # Update booking status
    bookings_collection.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"paid": True}}
    )

    # Create transaction record
    transaction = {
        "user_id": booking["user_id"],
        "amount": price,
        "transaction_type": "payment",
        "status": "completed",
        "description": f"Payment for service {service['name']}",
        "created_at": datetime.utcnow()
    }
    transactions_collection.insert_one(transaction)

    return {"message": "Payment successful"}


# Mark booking as paid via cash on delivery
def mark_cash_on_delivery(booking_id: str):
    booking = bookings_collection.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        return {"error": "Booking not found"}

    bookings_collection.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"paid": True}}
    )
    return {"message": "Booking marked as paid via cash on delivery"}
