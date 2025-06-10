from pydantic import BaseModel

class DocumentBase(BaseModel):
    doc_name: str
    doc_type: int
    description: str