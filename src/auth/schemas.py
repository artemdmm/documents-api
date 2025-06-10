from pydantic import BaseModel, EmailStr
from datetime import date

class UserBase(BaseModel):
    email: EmailStr
    password: str

class UserRegistration(UserBase):
    name: str

class UserResponse(BaseModel):
    email: EmailStr
    name: str
    registration_date: date

class UserNameChange(BaseModel):
    email: EmailStr
    name: str

class UserPermissions(BaseModel):
    email: EmailStr
    permissions: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None