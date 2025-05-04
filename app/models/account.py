from datetime import datetime
from typing import Literal
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class Account(BaseModel):
    id: str = None
    user_id: str
    account_type: Literal["savings", "current"] = "savings"
    account_number: str = Field(..., min_length=10, max_length=10)
    balance: Decimal = Field(default=Decimal("0.00"))
    is_active: bool = True
    currency: str = "NGN"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders = {ObjectId: str, Decimal: str}
    )