from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from ...schemas.user import UserCreate, Token, NewPassword
from ...services.auth import create_user, get_user_by_email, resend_verification_email, generate_password_reset, reset_user_password
from ...core.security import verify_password, create_access_token, verify_user
from ...database import users_collection


router = APIRouter(prefix="/auth", tags=["auth"])



@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    return await create_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        phone_number=user_data.phone_number
    )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your email first"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/verify")
async def verify_email(token: str):
    if await verify_user(token):
        return {"message": "Email verified successfully"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid verification token"
    )

@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(email: EmailStr):
    return await resend_verification_email(email)

@router.post("/password-reset/request")
async def request_password_reset(email: EmailStr):
    if await generate_password_reset(email):
        return {"message": "Password reset email sent"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid email or unverified account"
    )

@router.get("/password-reset/verify")
async def verify_reset_token(reset_token: str):
    user_data = await users_collection.find_one({"reset_token": reset_token})
    if user_data:
        return {"message": "Password reset token verified successfully"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid verification token"
    )

@router.post("/password-reset/confirm")
async def reset_password(password_data: NewPassword):
    if await reset_user_password(password_data.token, password_data.new_password):
        return {"message": "Password reset successfully"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired reset token"
    )