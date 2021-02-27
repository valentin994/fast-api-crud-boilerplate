from fastapi import FastAPI, Request, Depends, Response, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from models import User, Message
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
from kafka import KafkaConsumer, KafkaProducer
import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from kafka_producer import send_one
from pymongo import MongoClient

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


async def kafka_consume(websocket: WebSocket):
    """Consumer for websocket to stream to the frontend, connecting on default kafka consumer (has to be up and running for it to work)

    Args:
        websocket (WebSocket): websocket for clients to connect to
    """
    consumer = AIOKafkaConsumer(
        "quickstart-events",
        bootstrap_servers="localhost:9092",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            await websocket.send_text(msg.value.decode("utf-8"))
    finally:
        await consumer.stop()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """This websocket is used for broadcasting messages from kafka stream

    Args:
        websocket (WebSocket): websocket for clients to connect to
    """
    await websocket.accept()
    await kafka_consume(websocket)


@app.post("/send_message/")
async def send_msg(message: dict):
    """Endpoint for users to send messages, messages from client have to have sender, destination and message as data parameter.

    Args:
        message (dict): message model for kafka producer to send a message

    Returns:
        [int]: 200 if successful
    """
    await send_one(message)
    return 200


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/user", response_description="Users fetched", response_model=List[User])
async def get_users() -> List[User]:
    """Get all users in database

    Raises:
        HTTPException: If there are no users return 404

    Returns:
        List[User]: List of users stored in database
    """
    response = await get_all_users()
    if response:
        return response
    raise HTTPException(status_code=404, detail="Users not found")


@app.post(
    "/register/",
    response_description="User registered",
    response_model=User,
    response_model_exclude={"password"},
)
async def add_user(
    user: User,
    response: Response,
) -> User:
    """Register new user. User model defined in models, all fields are mandatory.
    Password is hashed.

    Args:
        user (User): User model(name, password, email)
        response (Response): Returns user without password
        Authorize (AuthJWT, optional): [description]. Defaults to Depends().

    Raises:
        HTTPException: If user already exists with the email raise 400 http exception

    Returns:
        User: User model without password
    """
    user.password = pbkdf2_sha256.hash(user.password.get_secret_value())
    new_user = await register_user(user.dict())
    if new_user:
        return user
    raise HTTPException(status_code=400, detail="Email already in use")


@app.post("/login/", response_model=User, response_model_exclude={"password"})
async def login_user(
    login: dict, response: Response, Authorize: AuthJWT = Depends()
) -> User:
    """Login user and set access token for next requests. Token is built from email.

    Args:
        login (dict): Login information, email & password
        response (Response): Return user without password
        Authorize (AuthJWT, optional): Set jwt

    Raises:
        HTTPException: If wrong info is given raise 401

    Returns:
        User: Name & email, set access token
    """
    user = await find_user(login["email"])
    if pbkdf2_sha256.verify(login["password"], user["password"]):
        access_token = Authorize.create_access_token(subject=user["email"])
        Authorize.set_access_cookies(access_token)
        return user
    raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/jwt_login", response_model=User, response_model_exclude={"password"})
async def jwt_login_user(Authorize: AuthJWT = Depends()) -> User:
    """Login via JWT

    Args:
        Authorize (AuthJWT, optional): Token to login with, decrypts to email

    Raises:
        HTTPException: IF token is not valid return 401

    Returns:
        User: Name & mail
    """
    Authorize.jwt_required()
    email = Authorize.get_jwt_subject()
    user = await find_user(email)
    if user:
        return user
    raise HTTPException(status_code=401, detail="Unauthorized")


@app.get(
    "/user/{email}",
    response_description="Found user",
    response_model=User,
    response_model_exclude={"password"},
)
async def get_one_user(email: str) -> User:
    """Find user by email

    Args:
        email (str): user email

    Raises:
        HTTPException: If there are no users return 404

    Returns:
        User: Name & email
    """
    user = await find_user(email)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User was not found")


@app.delete("/user/{email}", response_description="Delete user")
async def delete_user(email: str) -> str:
    """Remove user entry in db

    Args:
        email (str): email of user to be removed

    Raises:
        HTTPException: 404 if user does not exist

    Returns:
        str: Confirmation message
    """
    deleted_user = remove_user(email)
    if deleted_user:
        return "User deleted successfully"
    raise HTTPException(status_code=404, detail="User not found")


@app.put(
    "/user/{email}",
    response_description="Updated user.",
    response_model=User,
    response_model_exclude={"password"},
)
async def update_user(email: str, data: dict) -> User:
    """Update user entry

    Args:
        email (str): email of user to be updated
        data (dict): data that should be updated

    Raises:
        HTTPException: 404 if user is not found

    Returns:
        User: New updated user
    """
    user = await find_and_update_user(email, data)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")
