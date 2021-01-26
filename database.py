from models import User
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


async def register_user(data: dict) -> User:
    user = await users_collection.find_one({"email": data["email"]})
    if user is None:
        new_user = await users_collection.insert_one(data)
        response = await users_collection.find_one({"_id": new_user.inserted_id})
        return response
    return False


async def find_user(email: str) -> User:
    response = await users_collection.find_one({"email": email})
    return response


async def remove_user(email: str) -> bool:
    user = await users_collection.find_one({"email": email})
    if user:
        await users_collection.delete_one({"email": email})
        return True
    return False


async def find_and_update_user(email: str, data: dict) -> User:
    if len(data) < 1:
        return False
    user = await users_collection.find_one({"email": email})
    if user or list(data.keys()):
        await users_collection.update_one({"email": email}, {"$set": data})
        return await users_collection.find_one({"email": email})
    return False
