import motor.motor_asyncio
from bson.objectid import ObjectId

client = motor.motor_asyncio.AsyncIOMotorClient()

users_db = client.users
users_collection = users_db["users"]

# User DB CRUD Operations

async def get_all_users():
    users = []
    async for user in users_collection.find():
        users.append(user)
    return users