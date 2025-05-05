from fastapi import HTTPException, status, Depends
from typing import Literal
from datetime import datetime
from bson import ObjectId
from bson.decimal128 import Decimal128
import random
import string

from ..database import accounts_collection, users_collection
from ..models.user import User
from ..services.auth import get_current_user
from ..models.account import Account

async def generate_account_number() -> str:
    while True:
        account_number = ''.join(random.choices(string.digits, k=10))

        existing = await accounts_collection.find_one({"account_number": account_number})
        if not existing:
            return account_number
        
async def create_account_for_user(
        bvn: str, 
        account_type: Literal["savings", "current"] = "savings",
        current_user: User = Depends(get_current_user),
    ) -> dict:
    if not current_user.bvn:
        await users_collection.update_one(
            {"_id": ObjectId(current_user.id)},
            {
                "$set": {"bvn": bvn},
                "$currentDate": {"updated_at": True}
            }
        )
    
    elif current_user.bvn != bvn:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The BVN provided does not match your registered BVN."
        )
    
    existing_account = await accounts_collection.find_one({
        "user_id": str(current_user.id),
        "account_type": account_type
    })
    
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already have a {account_type} account."
        )
    
    new_account = {
        "user_id": str(current_user.id),
        "account_type": account_type,
        "account_number": await generate_account_number(),
        "balance": 0.0,
        "is_active": True,
        "currency": "NGN",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    result = await accounts_collection.insert_one(new_account)
    new_account["_id"] = str(result.inserted_id)
    return new_account

async def get_user_account(user_id: str) -> Account:
    account_data = await accounts_collection.find_one({"user_id": user_id})
    if not account_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    if isinstance(account_data.get("balance"), Decimal128):
        account_data["balance"] = account_data["balance"].to_decimal()
    account_data['id'] = str(account_data['_id']) 
    return Account(**account_data)

async def get_user_balance(user_id: str) -> float:
    account = await get_user_account(user_id)
    return account.balance