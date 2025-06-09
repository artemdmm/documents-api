from sqlmodel import SQLModel, Field
from datetime import date
from typing import Optional

class DocumentBase(SQLModel):
    doc_name: str
    doc_type: int = Field(default=1, foreign_key="doctypes.id")
    description: str

    #class Config:
    #    json_schema_extra = {
    #        "example": {
    #            "doc_name": "Document title",
    #            "doc_type": 1,
    #            "description": "Description of the document",
    #        }
    #    }

class DocumentModel(DocumentBase, table=True):
    __tablename__ = 'documents'
    id: int = Field(default=None, primary_key=True)
    slug: str = Field(nullable=False, unique=True)
    owner_id: int = Field(default=None, foreign_key="users.id")
    creation_date: date
    path: Optional[str]

    #class Config:
    #    json_schema_extra = {
    #        "example": {
    #            "id": 1,
    #            "slug": "document-title",
    #            "doc_name": "Document title",
    #            "doc_type": 1,
    #            "creation_date": "2024.05.05",
    #            "description": "Description of the document",
    #        }
    #    }

class DocumentCreate(DocumentBase):
    pass