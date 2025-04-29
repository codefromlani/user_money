from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from schemas.account import AccountCreatePayload, AccountCreate, Account
from database import accounts_collection
from schemas.transaction import DepositTransactionPayload, WithdrawTransactionPayload
from schemas.user import User
from serializers import account_serializer
from bson.objectid import ObjectId


class AccountService:

    @staticmethod
    def create_account(account_data: AccountCreatePayload, user: User) -> Account:
        account_data = account_data.model_dump()
        account_with_defaults = Account(
            **account_data,
            user_id=user.id,
            balance=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        account_id = accounts_collection.insert_one(jsonable_encoder(account_with_defaults)).inserted_id
        account = accounts_collection.find_one({"_id": account_id})
        return account_serializer(account)


    @staticmethod
    def get_account(user: User):
        account = accounts_collection.find_one({"user_id": user.id})
        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        return account_serializer(account)
    

    @staticmethod
    def get_account_by_id(account_id: str):
        account = accounts_collection.find_one({"_id": ObjectId(account_id)})
        return account_serializer(account)

    @staticmethod
    def deposit_fund(deposit_payload: DepositTransactionPayload, account_id):
        account = AccountService.get_account_by_id(account_id)
        old_balance = float(account.balance)
        new_balance = old_balance + float(deposit_payload.amount)
        account.balance = new_balance
        account = accounts_collection.find_one_and_update(
            {"_id": ObjectId(account.id)},
            {"$set": {"balance": new_balance}}
        )
        return "successful"

    @staticmethod
    def withdraw_fund(withdraw_payload: WithdrawTransactionPayload, account_id: str, current_user: User):
        account = AccountService.get_account_by_id(account_id)
        
        # Verify account ownership
        if account.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only withdraw from your own account"
            )
        
        # Check if sufficient balance
        old_balance = float(account.balance)
        withdrawal_amount = float(withdraw_payload.amount)
        
        if withdrawal_amount > old_balance:
            raise HTTPException(
                status_code=400,
                detail="Insufficient funds for withdrawal"
            )
        
        new_balance = old_balance - withdrawal_amount
        account = accounts_collection.find_one_and_update(
            {"_id": ObjectId(account.id)},
            {"$set": {"balance": new_balance}}
        )
        return "Withdrawal successful"


account_service = AccountService()
