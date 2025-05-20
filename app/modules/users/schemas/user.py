from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    role_id: Optional[int] = None

class User(UserBase):
    id: int
    is_active: bool
    role_id: Optional[int] = None

    class Config:
        from_attributes = True 