from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    name: str
    role: str

class UserCreate(UserBase):
    password: str
    created_by: Optional[str] = None

class UserUpdate(UserBase):
    updated_by: Optional[str] = None

class UserOut(UserBase):
    id: int
    created_date: Optional[str]
    updated_date: Optional[str]

    class Config:
        orm_mode = True