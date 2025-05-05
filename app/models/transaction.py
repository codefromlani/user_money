from datetime import datetime
from typing import Optional, Literal
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class Transaction(BaseModel):
    id: str = None
    account_id: str
    transaction_type: Literal["deposit", "withdrawal", "transfer"]
    amount: Decimal
    description: Optional[str] = None
    balance_before: Decimal
    balance_after: Decimal
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: Literal["pending", "completed", "failed"] = "pending"
    recipient_account_id: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders = {ObjectId: str}
    )