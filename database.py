from pymongo import MongoClient
from bson.objectid import ObjectId
from models import User
from pymongo.errors import DuplicateKeyError

client = MongoClient("mongodb://localhost:27017")

users_db = client.users
users_collection = users_db.get_collection("users")

#Run only once for setup

#users_collection.create_index("email", unique=True)


# User DB CRUD Operations

def get_all_users():
    users = []
    for user in users_collection.find():
        users.append(user_helper(user))
    return users

def register_user(user) -> dict: 
    try:   
        new_user = users_collection.insert_one(user)
        added_user = users_collection.find_one({"_id": new_user.inserted_id})
    except DuplicateKeyError:
        return "Email already exists"
    return user_helper(added_user)

def find_user(email: str) -> dict:
    user = users_collection.find_one({"email": email})
    return user_helper(user)

def remove_user(email: str):
    user = users_collection.find_one({"email": email})
    if user:
        users_collection.delete_one({"email": email})
        return True
    return False

def find_and_update_user(email: str, data: dict):
    if len(data)<1:
        return False
    user = users_collection.find_one({"email": email})
    if user or list(data.keys()):
        return True
    users_collection.update_one({"email": email},
                                        {"$set": data})
    return False


def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "password": user["password"]
    }