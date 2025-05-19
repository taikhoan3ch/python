from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class BusinessBase(BaseModel):
    name: str
    email: EmailStr
    description: Optional[str] = None

class BusinessCreate(BusinessBase):
    pass

class BusinessResponse(BusinessBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    view_count: int

    class Config:
        from_attributes = True 