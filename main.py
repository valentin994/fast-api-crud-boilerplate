from fastapi import FastAPI, Body
import uvicorn
from fastapi.encoders import jsonable_encoder
from models import (User, 
                    ResponseModel,
                    ErrorResponseModel)

from database import (get_all_users,
                      register_user,
                      )
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def homepage():
    return """
    <html>
        <head>
            <title>Available Routes</title>
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
            <style>
                html, body{
                    height:100%;
                }
                #title{
                    font-size:32px;
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <div style="height:100%" class="bg-dark">
                <p id="title" class="text-success"> List of routes</p>
                <div class="container">
                    <ul class="list-group">
                        <li class="list-group-item list-group-item-success">GET "/users" -> Fetches all users from database</li>
                        <li class="list-group-item list-group-item-success">POST "/users/" -> Registers a user, return 404 if user already exists</li>
                    </ul> 
                </div>
            </div>
        </body>
    </html>
    """


@app.get("/user", response_description="Users fetched")
async def get_users():
    users = get_all_users()
    if users:
        return ResponseModel(users, "Successfully fetched users")
    return ResponseModel(users, "There are no users in the database")

@app.post("/user/", response_description="User registered")
async def add_user(user: User):
    new_user = register_user(jsonable_encoder(user))
    if(new_user == "Email already exists"):
        return ErrorResponseModel("An error occurred", 404, "This email adress is already in use.")
    return ResponseModel(new_user, "User added successfully")

@app.get("/user/{email}")
async def get_one_user():
    return 1
#delete user

#update user



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info", reload=True)
