from sqlmodel import Field, SQLModel
from datetime import date
from typing import Optional

class DocumentModel(SQLModel, table=True):
    __tablename__ = 'documents'
    __table_args__ = {'extend_existing': True}
    id: int = Field(default=None, primary_key=True)
    doc_name: str
    doc_type: int = Field(default=1, foreign_key="doctypes.id")
    description: str
    slug: str = Field(nullable=False, unique=True)
    owner_id: int = Field(default=None, foreign_key="users.id")
    creation_date: date
    path: Optional[str]

class DocTypeModel(SQLModel, table=True):
    __tablename__ = 'doctypes'
    id: int = Field(default=None, primary_key=True)
    title: str