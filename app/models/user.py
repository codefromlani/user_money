from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class User(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    email: EmailStr
    password_hash: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders = {ObjectId: str}
    )