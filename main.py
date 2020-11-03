from fastapi import FastAPI
import uvicorn
from models import User, ResponseModel
from database import get_all_users


app = FastAPI()


@app.get("/")
async def read_root():
    return {
        "routes": [
            {"GET":["/user"]},
            {"POST":["/user"]}
        ]
    }

@app.get("/user", response_description="Users fetched")
async def get_users():
    users = await get_all_users()
    if users:
        return ResponseModel(users, "Successfully fetched users")
    return ResponseModel(users, "There are no users in the database")

#get one user

#delete user

#update user

@app.post("/user", response_description="User registered")
async def register_user(user: User):
    return ResponseModel(user, "User added successfully")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")
