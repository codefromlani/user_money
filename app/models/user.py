from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, ConfigDict, validator
from typing import Optional


class User(BaseModel):
    id: str = None
    email: EmailStr
    password_hash: str
    full_name: str
    is_active: bool = True
    is_verified: bool = False
    verification_token: Optional[str] = None
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None
    bvn: Optional[str] = None
    phone_number: str 
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('bvn')
    def validate_bvn(cls, v):
        if v is not None and len(v) != 11:
            raise ValueError("BVN must be exactly 11 character")
        return v 
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) < 11 or len(v) > 15:
            raise ValueError("Phone number must be between 11 and 15 characters.")
        return v

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders = {ObjectId: str}
    )