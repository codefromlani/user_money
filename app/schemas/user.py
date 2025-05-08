from typing import Optional
from pydantic import BaseModel, EmailStr, Field, constr


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    phone_number: str = constr(strict=True, min_length=11, max_length=15)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(..., min_length=2)
    phone_number: Optional[str] = constr(strict=True, min_length=11, max_length=15)


class NewPassword(BaseModel):
    token: str
    new_password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"