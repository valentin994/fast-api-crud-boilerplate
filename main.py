from fastapi import FastAPI, Body
import uvicorn
from fastapi.encoders import jsonable_encoder
from models import (User, 
                    ResponseModel,
                    ErrorResponseModel)

from database import (get_all_users,
                      register_user,
                      )


app = FastAPI()


@app.get("/user", response_description="Users fetched")
async def get_users():
    users = get_all_users()
    if users:
        return ResponseModel(users, "Successfully fetched users")
    return ResponseModel(users, "There are no users in the database")

@app.post("/user/", response_description="User registered")
def add_user(user: User):
    new_user = register_user(jsonable_encoder(user))
    if(new_user == "Email already exists"):
        return ErrorResponseModel("An error occurred", 404, "This email adress is already in use.")
    return ResponseModel(new_user, "User added successfully")

#get one user

#delete user

#update user



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info", reload=True)
