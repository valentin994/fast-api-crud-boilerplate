from fastapi import FastAPI, Request, Depends, Response, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
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
from kafka import KafkaConsumer, KafkaProducer
import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

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


async def kafka_produce():
    producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
    await producer.start()
    while True:
        data = await websocket.receive_text()
        if data:
            await producer.send_and_wait("quickstart-events", b"hello")


async def kafka_consume(websocket: WebSocket):
    consumer = AIOKafkaConsumer(
        "quickstart-events",
        bootstrap_servers="localhost:9092",
    )
    await consumer.start()
    async for msg in consumer:
        await websocket.send_text("hello")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await kafka_consume(websocket)


# @app.post("/send_message")
# async def send_msg(message: str, sender: str):


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/user", response_description="Users fetched", response_model=List[User])
async def get_users() -> List[User]:
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
    Authorize: AuthJWT = Depends(),
) -> User:
    user.password = pbkdf2_sha256.hash(user.password.get_secret_value())
    new_user = await register_user(user.dict())
    if new_user:
        return user
    raise HTTPException(status_code=400, detail="Email already in use")


@app.post("/login/", response_model=User, response_model_exclude={"password"})
async def login_user(login: dict, Authorize: AuthJWT = Depends()) -> User:
    user = await find_user(login["email"])
    if pbkdf2_sha256.verify(login["password"], user["password"]):
        access_token = Authorize.create_access_token(subject=user["email"])
        Authorize.set_access_cookies(access_token)
        return user
    raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/jwt_login", response_model=User, response_model_exclude={"password"})
async def login_user(Authorize: AuthJWT = Depends()) -> User:
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
    user = await find_user(email)
    if user:
        return user
    return HTTPException(status_code=404, detail="User was not found")


@app.delete("/user/{email}", response_description="Delete user")
async def delete_user(email: str) -> str:
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
    user = await find_and_update_user(email, data)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")
