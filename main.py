from fastapi import FastAPI, Request, Depends, Response, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
import uvicorn
from models import User
from database import (
    get_all_users,
    register_user,
    find_user,
    remove_user,
    find_and_update_user,
)
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from passlib.hash import pbkdf2_sha256


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_secure: bool = False
    authjwt_cookie_csrf_protect: bool = False


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/user", response_description="Users fetched", response_model=List[User])
async def get_users():
    response = await get_all_users()
    if response:
        return response
    raise HTTPException(status_code=404, detail="Users not found")


@app.post("/register/", response_description="User registered")
async def add_user(user: User, response: Response, Authorize: AuthJWT = Depends()):
    user.password = pbkdf2_sha256.hash(user.password.get_secret_value())
    new_user = register_user(jsonable_encoder(user))
    if new_user:
        return "Successfully registered"
    raise HTTPException(status_code=400, detail="Email already in use")


@app.post("/login/", response_model=User)
async def login_user(login: dict, Authorize: AuthJWT = Depends()):
    user = find_user(login["email"])
    if pbkdf2_sha256.verify(login["password"], user["password"]):
        access_token = Authorize.create_access_token(subject=user["email"])
        Authorize.set_access_cookies(access_token)
        return user
    raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/jwt_login", response_model=User)
async def login_user(user: User, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    email = Authorize.get_jwt_subject()
    user = find_user(email)
    if user:
        return user
    raise HTTPException(status_code=401, detail="Unauthorized")


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
