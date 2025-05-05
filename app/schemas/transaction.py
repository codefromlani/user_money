from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class TransactionRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None


class TransferRequest(BaseModel):
    to_account_number: str = Field(..., min_length=10, max_length=10)
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None