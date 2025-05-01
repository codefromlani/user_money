import os
from dotenv import load_dotenv
import motor.motor_asyncio

load_dotenv()


client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.user_money_v2


users_collection = db.get_collection("users")
accounts_collection = db.get_collection("accounts")
transactions_collection = db.get_collection("transactions")
