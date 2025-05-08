from fastapi import HTTPException, status
from typing import Optional, List
from bson import ObjectId
from bson.decimal128 import Decimal128
from decimal import Decimal

from ..models.transaction import Transaction
from ..models.account import Account
from .account import get_user_account
from ..database import db, transactions_collection, accounts_collection


async def user_deposit(user_id: str, amount: Decimal, description: Optional[str] = None) -> Transaction:
    account = await get_user_account(user_id)

    if not account.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account ID is missing or invalid"
        )
    balance_before = account.balance
    balance_after = balance_before + amount

    transaction = Transaction(
        account_id=account.id,
        transaction_type="deposit",
        amount=amount,
        description=description,
        balance_before=balance_before,
        balance_after=balance_after
    )

    async with await db.client.start_session() as session:
        async with session.start_transaction():
            await accounts_collection.update_one(
                {"_id": ObjectId(account.id)},
                {
                    "$set": {"balance": Decimal128(balance_after)},
                    "$currentDate": {"updated_at": True}
                }
            )

            transaction_dict = transaction.dict(exclude={'id'})
            for field in ['amount', 'balance_before', 'balance_after']:
                if field in transaction_dict and isinstance(transaction_dict[field], Decimal):
                    transaction_dict[field] = Decimal128(transaction_dict[field])

            result = await transactions_collection.insert_one(transaction_dict)
            transaction.id = str(result.inserted_id)
            transaction.status = "completed"

            await transactions_collection.update_one(
                {"_id": result.inserted_id},
                {"$set": {"status": "completed"}}
            )

        return transaction
    
async def user_withdrawal(user_id: str, amount: Decimal, description: Optional[str] = None):
    account = await get_user_account(user_id)
    if account.balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds"
        )
    
    balance_before = account.balance
    balance_after = balance_before - amount

    transaction = Transaction(
        account_id=account.id,
        transaction_type="withdrawal",
        amount=amount,
        description=description,
        balance_before=balance_before,
        balance_after=balance_after
    )

    async with await db.client.start_session() as session:
        async with session.start_transaction():
            await accounts_collection.update_one(
                {"_id": ObjectId(account.id)},
                {
                    "$set": {"balance": Decimal128(balance_after)},
                    "$currentDate": {"updated_at": True}
                }
            )

            transaction_dict = transaction.dict(exclude={'id'})
            for field in ['amount', 'balance_before', 'balance_after']:
                if field in transaction_dict and isinstance(transaction_dict[field], Decimal):
                    transaction_dict[field] = Decimal128(transaction_dict[field])

            result = await transactions_collection.insert_one(transaction_dict)
            transaction.id = str(result.inserted_id)
            transaction.status = "completed"

            await transactions_collection.update_one(
                {"_id": result.inserted_id},
                {"$set": {"status": "completed"}}
            )
    
    return transaction

async def user_transfer(
        from_user_id: str,
        to_account_number: str,
        amount: Decimal,
        description: Optional[str] = None
) -> Transaction:
    
    from_account = await get_user_account(from_user_id)
    if from_account.balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds"
        )
    
    to_account_data = await accounts_collection.find_one({"account_number": to_account_number})
    if not to_account_data:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipient account not found"
            )
    
    if isinstance(to_account_data.get("balance"), Decimal128):
        to_account_data["balance"] = to_account_data["balance"].to_decimal()

    to_account_data["id"] = str(to_account_data["_id"])
    to_account = Account(**to_account_data)

    if from_account.id == to_account.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transfer to same account"
        )
    
    sender_transaction = Transaction(
        account_id=from_account.id,
        transaction_type="transfer",
        amount=amount,
        description=description,
        balance_before=from_account.balance,
        balance_after=from_account.balance - amount,
        recipient_account_id=to_account.id
    )

    recipient_transaction = Transaction(
        account_id=to_account.id,
        transaction_type="transfer",
        amount=amount,
        description=f"Transfer from {from_account.account_number}",
        balance_before=to_account.balance,
        balance_after=to_account.balance + amount,
        recipient_account_id=from_account.id
    )

    async with await db.client.start_session() as session:
        async with session.start_transaction():
            await accounts_collection.update_one(
                {"_id": ObjectId(from_account.id)},
                {
                    "$set": {"balance": Decimal128(sender_transaction.balance_after)},
                    "$currentDate": {"updated_at": True}
                }
            )

            await accounts_collection.update_one(
                {"_id": ObjectId(to_account.id)},
                {
                    "$set": {"balance": Decimal128(recipient_transaction.balance_after)},
                    "$currentDate": {"updated_at": True}
                }
            )

            sender_dict = sender_transaction.dict(exclude={'id'})
            recipient_dict = recipient_transaction.dict(exclude={'id'})

            for field in ['amount', 'balance_before', 'balance_after']:
                sender_dict[field] = Decimal128(sender_dict[field])
                recipient_dict[field] = Decimal128(recipient_dict[field])

            sender_result = await transactions_collection.insert_one(sender_dict)
            recipient_result = await transactions_collection.insert_one(recipient_dict)

            sender_transaction.id = str(sender_result.inserted_id)
            recipient_transaction.id = str(recipient_result.inserted_id)

            sender_transaction.status = "completed"
            recipient_transaction.status = "completed"

            await transactions_collection.update_one(
                {"_id": sender_result.inserted_id},
                {"$set": {"status": "completed"}}
            )

            await transactions_collection.update_one(
                {"_id": recipient_result.inserted_id},
                {"$set": {"status": "completed"}}
            )

    return sender_transaction

async def get_user_transactions(
        user_id: str,
        skip: int = 0,
        limit: int = 10,
        transaction_type: Optional[str] = None
) -> List[Transaction]:
    account = await get_user_account(user_id)

    query = {"account_id": account.id}
    if transaction_type:
        query["transaction_type"] = transaction_type

    transactions = []
    transactions_cursor = transactions_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
    async for transaction in transactions_cursor:

        for field in ["amount", "balance_before", "balance_after"]:
            if isinstance(transaction.get(field), Decimal128):
                transaction[field] = transaction[field].to_decimal()
        transactions.append(Transaction(**transaction))

    return transactions