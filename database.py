from pymongo import MongoClient
from bson.objectid import ObjectId
from models import User
from pymongo.errors import DuplicateKeyError
import motor.motor_asyncio
from typing import List

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")


users_db = client.users
users_collection = users_db.users

# Run only once for setup

# users_collection.create_index("email", unique=True)


# User DB CRUD Operations


async def get_all_users() -> List[User]:
    cursor = users_collection.find({})
    data = await cursor.to_list(length=1000)
    response = [user for user in data]
    return response


async def register_user(user: dict) -> User:
    user = await users_collection.find_one({"email": user["email"]})
    if user:
        return False
    new_user = await users_collection.insert_one(user)
    added_user = await users_collection.find_one({"_id": new_user.inserted_id})
    return user


def find_user(email: str) -> dict:
    user = users_collection.find_one({"email": email})
    return user


def remove_user(email: str):
    user = users_collection.find_one({"email": email})
    if user:
        users_collection.delete_one({"email": email})
        return True
    return False


def find_and_update_user(email: str, data: dict):
    if len(data) < 1:
        return False
    user = users_collection.find_one({"email": email})
    if user or list(data.keys()):
        users_collection.update_one({"email": email}, {"$set": data})
        return users_collection.find_one({"email": email})
    return False


def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "password": user["password"],
    }