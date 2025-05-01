from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, ConfigDict, constr
from typing import Optional


class User(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    email: EmailStr
    password_hash: str
    full_name: str
    is_active: bool = True
    is_verified: bool = False
    verification_token: Optional[str] = None
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None
    bvn: str = constr(strict=True, min_length=11, max_length=11, regex=r'^\d{11}$')
    phone_number: str = constr(strict=True, min_length=11, max_length=15, regex=r'^\+?\d{11,15}$')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders = {ObjectId: str}
    )