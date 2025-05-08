from fastapi import APIRouter, Depends
from typing import List, Optional

from ...models.transaction import Transaction
from ...models.user import User
from ...schemas.transaction import TransactionRequest, TransferRequest
from ...services.auth import get_current_user
from ...services.transaction import user_deposit, user_withdrawal, user_transfer, get_user_transactions


router = APIRouter(prefix="/transaction", tags=["transaction"])

@router.post("/deposit", response_model=Transaction)
async def deposit(deposit_data: TransactionRequest, current_user: User = Depends(get_current_user)):
    return await user_deposit(current_user.id, deposit_data.amount, deposit_data.description)

@router.post("/withdraw", response_model=Transaction)
async def withdraw(withdraw_data: TransactionRequest, current_user: User = Depends(get_current_user)):
    return await user_withdrawal(current_user.id, withdraw_data.amount, withdraw_data.description)

@router.post("/transfer", response_model=Transaction)
async def transfer(transfer_data: TransferRequest, current_user: User = Depends(get_current_user)):
    return await user_transfer(current_user.id, transfer_data.to_account_number, transfer_data.amount, transfer_data.description)
    
@router.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    skip: int = 0,
    limit: int = 10,
    transaction_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    return await get_user_transactions(current_user.id, skip, limit, transaction_type)