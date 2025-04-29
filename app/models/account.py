from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class Account(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    user_id: ObjectId
    balance: Decimal = Field(default=Decimal("0.00"))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders = {ObjectId: str, Decimal: str}
    )