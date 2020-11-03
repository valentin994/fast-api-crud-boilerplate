import motor.motor_asyncio
from bson.objectid import ObjectId
from models import User

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")

users_db = client.marketplace_services
users_collection = users_db.get_collection("users")

# User DB CRUD Operations

async def get_all_users():
    print("hey")
    users = []
    async for user in users_collection.find():
        users.append(user)
    return users

async def register_user(user: User):
    users_collection.create_index("email")
    user = await users_collection.insert_one(user.dict())
    print(user.dict())
    return user