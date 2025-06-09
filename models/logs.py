from sqlmodel import SQLModel, Field, JSON, Column
from datetime import datetime
import uuid

class ApiLog(SQLModel, table=True):

    __tablename__ = 'api_logs'
    id: int | None = Field(default=None, primary_key=True)
    api_key: uuid.UUID | None
    ip_address: str
    path: str
    method: str
    status_code: int
    request_body: dict | list | None = Field(default=None, sa_column=Column(JSON))
    response_body: dict | list | None = Field(default=None, sa_column=Column(JSON))
    query_params: dict | None = Field(default=None, sa_column=Column(JSON))
    path_params: dict | None = Field(default=None, sa_column=Column(JSON))
    process_time: float
    created_at: datetime

    class Config:
        allow_arbitrary_types = True