from fastapi import FastAPI, Request, Depends, Response, HTTPException
import uvicorn
from fastapi.encoders import jsonable_encoder
from models import User, ResponseModel, ErrorResponseModel
from database import (
    get_all_users,
    register_user,
    find_user,
    remove_user,
    find_and_update_user,
)
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from typing import List

app = FastAPI()


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


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
                        <li class="list-group-item list-group-item-success">GET "/user" -> Fetches all users from database</li>
                        <li class="list-group-item list-group-item-primary">POST "/user/" -> Registers a user, return 404 if user already exists</li>
                        <li class="list-group-item list-group-item-success">GET "/user/{email}" -> Find user by email, if there is no registered user with that email return 404.</li>
                        <li class="list-group-item list-group-item-danger">DELETE "/user/{email}" -> Delete user by email, if there is no registered user with that email return 404.</li>
                        <li class="list-group-item list-group-item-warning">PUT "/user/{email}" -> Updates user by email, if there is no registered user with that email return 404.</li>
                    </ul> 
                </div>
            </div>
        </body>
    </html>
    """


@app.get("/user", response_description="Users fetched", response_model=List[User])
async def get_users():
    users = get_all_users()
    if users:
        return users
    raise HTTPException(status_code=404, detail="Users not found")


@app.post("/user/", response_description="User registered", response_model=User)
async def add_user(user: User, response: Response, Authorize: AuthJWT = Depends()):
    new_user = register_user(jsonable_encoder(user))
    if new_user:
        access_token = Authorize.create_access_token(subject=user.email)
        response.set_cookie(key="access_token", value=access_token)
        return user
    raise HTTPException(status_code=400, detail="Email already in use")


@app.get("/user/{email}", response_description="Found user", response_model=User)
async def get_one_user(email: str):
    user = find_user(email)
    if user:
        return user
    return HTTPException(status_code=404, detail="User was not found")


@app.delete("/user/{email}", response_description="Delete user")
async def delete_user(email: str):
    deleted_user = remove_user(email)
    if deleted_user:
        return "User deleted successfully"
    raise HTTPException(status_code=404, detail="User not found")


@app.put("/user/{email}", response_description="Updated user.", response_model=User)
async def update_user(email: str, data: dict):
    user = find_and_update_user(email, data)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info", reload=True)
