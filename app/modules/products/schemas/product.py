from pydantic import BaseModel, Field
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0, le=1000000)  # Maximum price of 1 million
    stock: int = Field(ge=0, le=1000000)    # Maximum stock of 1 million

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0, le=1000000)
    stock: Optional[int] = Field(None, ge=0, le=1000000)

class Product(ProductBase):
    id: int
    created_by: int

    class Config:
        from_attributes = True 