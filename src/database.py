from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

engine = create_engine('postgresql+psycopg2://postgres:134251@localhost:5432/postgres')

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session