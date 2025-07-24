from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"
    TRANSFER = "transfer"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"
    APPROVED = "approved"
    DECLINED = "declined"

# class WalletTransaction(BaseModel):
#     id: str = Field(alias="_id")
#     user_id: str
#     amount: float
#     transaction_type: TransactionType
#     reference: str
#     description: Optional[str] = None
#     status: str = "completed"  # pending, completed, failed
#     created_at: datetime = Field(default_factory=datetime.utcnow)

class WalletTransaction(BaseModel):
    id: str
    user_id: str
    amount: float
    transaction_type: TransactionType
    status: TransactionStatus = TransactionStatus.COMPLETED
    reference: str
    description: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime


class WalletTransactionResponse(BaseModel):
    transactions: List[WalletTransaction]
    total: int
    page: int
    limit: int



class Wallet(BaseModel):
    user_id: str
    balance: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class TransactionHistoryResponse(BaseModel):
    transactions: List[WalletTransaction]
    total_count: int
    current_balance: float

class RecentTransactionsResponse(BaseModel):
    recent_transactions: List[WalletTransaction]
    uncompleted_count: int