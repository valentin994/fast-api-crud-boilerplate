from pydantic import BaseModel, SecretStr, EmailStr


class User(BaseModel):
    name: str
    email: EmailStr
    password: SecretStr

    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "johndoes@example.com",
                "password": "******"
            }
        }


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message
    }


def ErrorResponseModel(error, code, message):
    return {
        "error": error,
        "code": code,
        "message": message
    }
