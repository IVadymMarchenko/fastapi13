import pydantic
from pydantic import EmailStr, Field


class UserSchema(pydantic.BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=4, max_length=8)


class UserResponse(pydantic.BaseModel):
    id: int = 1
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class TokenUpdate(pydantic.BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

class RequestEmail(pydantic.BaseModel):
    email:EmailStr