from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, String, Integer, Date

from src.schemas.user import UserResponse


class CreateContactSchema(BaseModel):
    name: str = Field(max_length=30)
    surname: str = Field(max_length=30)
    phone: str = Field(max_length=(30))
    email: str = Field(max_length=30)
    birthday: date
    information: Optional[str] = Field(None, max_length=250)



class CreateContact(BaseModel):
    id: int = 1
    name: str
    surname: str
    phone: str
    email: str
    birthday: date
    information: str
    user: UserResponse | None

    class Config:
        from_attributes = True
