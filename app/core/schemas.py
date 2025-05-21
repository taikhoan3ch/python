from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

# User schemas
class UserBase(BaseModel):
    username: str
    role: str
    permission: str

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

# Company schemas
class CompanyBase(BaseModel):
    code: str
    name: str
    logo: Optional[str] = None
    images: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

class CompanyCreate(CompanyBase):
    id: str  # tax_code

class CompanyUpdate(CompanyBase):
    pass

class CompanyInDBBase(CompanyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Company(CompanyInDBBase):
    pass

# Product schemas
class ProductBase(BaseModel):
    code: str
    name: str
    thumbnail: Optional[str] = None
    images: Optional[str] = None
    description: Optional[str] = None

class ProductCreate(ProductBase):
    company_id: str

class ProductUpdate(ProductBase):
    pass

class ProductInDBBase(ProductBase):
    id: int
    company_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Product(ProductInDBBase):
    pass

# Item schemas
class ItemBase(BaseModel):
    key: str
    box_key: str

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemInDBBase(ItemBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class Item(ItemInDBBase):
    pass

# Batch operations
class BatchItemCreate(BaseModel):
    quantity: int
    box_key: str 