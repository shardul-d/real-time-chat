from sqlmodel import SQLModel, Field #pyright: ignore[reportUnknownVariableType]

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    password_hash: bytes = Field(nullable=False)
