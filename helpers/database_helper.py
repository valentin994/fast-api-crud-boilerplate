from pymongo import MongoClient
from bson.objectid import ObjectId


client = MongoClient("mongodb://localhost:27017")

users_db = client.users
users_collection = users_db.get_collection("users")

users_collection.delete_many({})
