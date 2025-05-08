from fastapi import APIRouter, Depends, status

from ...services.auth import get_current_user
from ...models.user import User
from ...models.account import Account
from ...schemas.account import CreateAccount
from ...services.account import create_account_for_user, get_user_account, get_user_balance


router = APIRouter(prefix="/account", tags=["account"])

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=Account)
async def create_account(
    data: CreateAccount,
    current_user: User = Depends(get_current_user),
):
    return await create_account_for_user(data.bvn, data.account_type, current_user)

@router.get("/view", response_model=Account)
async def get_account(current_user: User = Depends(get_current_user)):
    return await get_user_account(current_user.id)

@router.get("/balance")
async def get_balance(current_user: User = Depends(get_current_user)):
    balance = await get_user_balance(current_user.id)
    return {"balance": balance}