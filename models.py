from pydantic import BaseModel, SecretStr, EmailStr

class User(BaseModel):
    name: str
    email: EmailStr
    password: SecretStr
