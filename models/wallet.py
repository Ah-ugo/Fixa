from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


# Wallet Transaction Types
class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"


# Wallet Model
class Wallet(BaseModel):
    user_id: str
    balance: float = 0.0
    last_updated: datetime = datetime.utcnow()

# Wallet Transaction Model
class WalletTransaction(BaseModel):
    id: str
    user_id: str
    amount: float
    transaction_type: TransactionType
    reference: str  # Monnify Transaction Reference
    created_at: datetime = datetime.utcnow()