from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError
import secrets

from ..models.user import User
from ..database import users_collection
from ..core.email import send_verification_email, send_reset_email
from ..core.security import get_password_hash, SECRET_KEY, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def create_user(email: EmailStr, password: str, full_name: str, phone_number: str) -> dict:
    if await users_collection.find_one({"email": email}):
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    password_hash = get_password_hash(password)
    verification_token = secrets.token_urlsafe(32)

    new_user = User(
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        phone_number=phone_number,
        verification_token=verification_token
    )

    await users_collection.insert_one(new_user.dict(exclude={'id'}))

    try:
        await send_verification_email(new_user.email, verification_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification email: {str(e)}"
        )

    return new_user.dict(exclude={"password_hash", "verification_token"})

async def get_user_by_email(email: EmailStr) -> Optional[User]:
    user_data = await users_collection.find_one({"email": email})
    if user_data:
        user_data["id"] = str(user_data["_id"])
        return User(**user_data)
    return None

async def resend_verification_email(email: EmailStr):
    user_data = await get_user_by_email(email)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user_data.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    token = user_data.verification_token
    await send_verification_email(user_data.email, token)

    return {"message": "Verification email sent successfully"}

async def generate_password_reset(email: EmailStr) -> bool:
    user = await get_user_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_verified:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is not verified"
        )
    reset_token = secrets.token_urlsafe(32)
    reset_token_expires = datetime.utcnow() + timedelta(hours=1)

    await users_collection.update_one(
        {"email": email},
        {
            "$set": {
                "reset_token": reset_token,
                "reset_token_expires": reset_token_expires
            },
            "$currentDate": {"updated_at": True}
        }
    )

    await send_reset_email(email, reset_token)
    return True

async def reset_user_password(reset_token: str,new_password: str) -> bool:
    user_data = await users_collection.find_one({
            "reset_token": reset_token,
            "reset_token_expires": {"$gt": datetime.utcnow()}
        })

    if user_data:
        await users_collection.update_one(
            {"_id": user_data["_id"]},
            {
                "$set": {
                    "password_hash": get_password_hash(new_password),
                    "reset_token": None,
                    "reset_token_expires": None
                },
                "$currentDate": {"updated_at": True}
            }
        )
        return True
    return False

async def update_user(email: EmailStr, full_name: Optional[str], phone_number: Optional[str]) -> dict:
    user_data = await users_collection.find_one({"email": email})

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_fields = {}
    if full_name is not None:
        update_fields["full_name"] = full_name
    if phone_number is not None:
        update_fields["phone_number"] = phone_number

    if update_fields:
        await users_collection.update_one(
            {"_id": user_data["_id"]},
            {
                "$set": update_fields,
                "$currentDate": {"updated_at": True}
            }
        )
    return {"detail": "User updated successfully"}

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user