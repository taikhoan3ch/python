from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    role_id: Optional[int] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None

class User(UserBase):
    id: int
    is_active: bool
    role_id: Optional[int] = None

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    success: bool = True
    data: User

    class Config:
        from_attributes = True 