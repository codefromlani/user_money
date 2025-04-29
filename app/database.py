import os
from pymongo import mongo_client
from dotenv import load_dotenv

load_dotenv()

client = mongo_client.MongoClient(os.getenv("DB_URL"))

users_collection = client["user_money_v2"]["users"]