from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import jwt
from fastapi import HTTPException, status
import os 
from dotenv import load_dotenv

from ..database import users_collection


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create access token"
        )

async def verify_user(token: str) -> bool:
    user_data = await users_collection.find_one({"verification_token": token})
    if user_data:
        await users_collection.update_one(
            {"_id": user_data["_id"]},
            {
                "$set": {"is_verified": True, "verification_token": None},
                "$currentDate": {"updated_at": True}
            }
        )
        return True
    return False