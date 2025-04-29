from datetime import datetime
from typing import Optional, Literal
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class Transaction(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    user_id: ObjectId
    type: Literal["deposit", "withdrawal", "transfer"]
    amount: Decimal
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: Literal["pending", "completed", "failed"] = "pending"
    recipient_user_id: Optional[ObjectId] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders = {ObjectId: str, Decimal: str}
    )