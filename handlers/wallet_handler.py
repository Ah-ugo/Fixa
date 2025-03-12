from datetime import datetime
from db import wallets_collection, transactions_collection, bookings_collection
from bson.objectid import ObjectId


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


# Pay for a service using wallet balance
def pay_for_service(booking_id: str):
    booking = bookings_collection.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        return {"error": "Booking not found"}

    wallet = wallets_collection.find_one({"user_id": booking["user_id"]})
    if not wallet or wallet["balance"] < booking["price"]:
        return {"error": "Insufficient wallet balance"}

    wallets_collection.update_one(
        {"user_id": booking["user_id"]},
        {"$inc": {"balance": -booking["price"]}}
    )
    bookings_collection.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"paid": True}}
    )
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
