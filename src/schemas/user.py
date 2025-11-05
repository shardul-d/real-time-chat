from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)


class UserCreate(BaseModel):
    password: str = Field(..., min_length=8)


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True  # pyright: ignore[reportUnannotatedClassAttribute]
