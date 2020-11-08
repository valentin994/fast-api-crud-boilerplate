from pydantic import BaseModel, SecretStr, EmailStr, Field


class User(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: SecretStr = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "johndoes@example.com",
                "password": "password"
            }
        }


def ResponseModel(data, message):
    return {
        "data": [data],
        "status_code": 200,
        "message": message
    }


def ErrorResponseModel(error, code, message):
    return {
        "error": error,
        "status_code": code,
        "message": message
    }
