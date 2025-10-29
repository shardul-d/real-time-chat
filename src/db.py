from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import Engine
from src.core.config import config

engine: Engine = create_engine(
    url=config.DATABASE_URL, connect_args={"check_same_thread": False}, echo=True
)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
