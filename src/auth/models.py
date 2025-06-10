from sqlmodel import Field, SQLModel
from datetime import date
import uuid

class UserModel(SQLModel, table=True):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id: int = Field(default=None, primary_key=True)
    email: str = Field(nullable=False, unique=True)
    password: str
    user_uuid: uuid.UUID = Field(default_factory=uuid.uuid4, index=True, nullable=False)
    name: str
    registration_date: date = Field(default_factory=date.today, nullable=False)
    permissions: int = Field(default=1, foreign_key="permissions.id")

class PermissionModel(SQLModel, table=True):
    __tablename__ = 'permissions'
    id: int = Field(default=None, primary_key=True)
    title: str