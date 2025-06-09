from sqlmodel import SQLModel, Field

class DocTypeModel(SQLModel, table=True):
    __tablename__ = 'doctypes'
    id: int = Field(default=None, primary_key=True)
    title: str