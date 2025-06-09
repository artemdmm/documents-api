from sqlmodel import SQLModel, Field

class PermissionModel(SQLModel, table=True):
    __tablename__ = 'permissions'
    id: int = Field(default=None, primary_key=True)
    title: str