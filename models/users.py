from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field
from datetime import date

import uuid

class UserBase(SQLModel):
    email: EmailStr = Field(nullable=False, unique=True)
    password: str

class UserModel(UserBase, table=True):
    __tablename__ = 'users'
    id: int = Field(default=None, primary_key=True)
    user_uuid: uuid.UUID = Field(default_factory=uuid.uuid4, index=True, nullable=False)
    name: str
    registration_date: date = Field(default_factory=date.today, nullable=False)
    permissions: int = Field(default=1, foreign_key="permissions.id")

class UserRegistration(UserBase):
    name: str

class UserResponse(SQLModel):
    email: EmailStr
    name: str
    registration_date: date

class UserNameChange(SQLModel):
    email: EmailStr
    name: str

class UserPermissions(SQLModel):
    email: EmailStr
    permissions: int