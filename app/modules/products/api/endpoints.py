from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.modules.common.config.database import get_db
from app.modules.common.middleware.auth_middleware import check_permissions
from app.modules.products.schemas.product import Product, ProductCreate
from app.modules.products.services.product_service import ProductService

router = APIRouter()

@router.post("/", response_model=Product)
@check_permissions(["create_product"])
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new product. Requires 'create_product' permission.
    """
    return ProductService.create_product(db=db, product=product)

@router.get("/", response_model=List[Product])
@check_permissions(["read_product"])
def get_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all products. Requires 'read_product' permission.
    """
    return ProductService.get_products(db=db, skip=skip, limit=limit)

@router.put("/{product_id}", response_model=Product)
@check_permissions(["update_product"])
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Update a product. Requires 'update_product' permission.
    """
    return ProductService.update_product(db=db, product_id=product_id, product=product)

@router.delete("/{product_id}")
@check_permissions(["delete_product"])
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a product. Requires 'delete_product' permission.
    """
    return ProductService.delete_product(db=db, product_id=product_id) 