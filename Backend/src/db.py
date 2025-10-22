from sqlmodel import SQLModel, create_engine
from sqlalchemy import Engine
from src import models # pyright: ignore[reportUnusedImport]
import os

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH: str = os.path.join(BASE_DIR, "chatapp.db")
DATABASE_URL: str = f"sqlite:///{DB_PATH}"
  
engine: Engine = create_engine(
  DATABASE_URL, 
  connect_args={"check_same_thread": False},
  echo=True
)

def create_db_and_tables() -> None:
  SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
  create_db_and_tables()
  