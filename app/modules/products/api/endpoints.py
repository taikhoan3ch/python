from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.modules.common.config.database import get_db
from app.modules.common.middleware.auth_middleware import check_permissions
from app.modules.products.schemas.product import Product, ProductCreate, ProductUpdate
from app.modules.products.services.product_service import ProductService
from app.modules.common.utils.response import StandardResponse
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=Dict[str, Any])
@check_permissions(["create_product"])
def create_product(
    request: Request,
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new product. Requires 'create_product' permission.
    """
    try:
        user_id = request.state.user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
            
        created_product = ProductService.create_product(db=db, product=product, user_id=user_id)
        return StandardResponse.success(
            data=created_product,
            message="Product created successfully"
        )

    except ValueError as e:
        logger.error(f"Validation error creating product: {str(e)}")
        return StandardResponse.error(message=str(e))

    except Exception as e:
        logger.exception("Unhandled error while creating product")
        return StandardResponse.error(message="An unexpected error occurred")


@router.get("/", response_model=List[Product])
@check_permissions(["read_product"])
def get_products(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all products. Requires 'read_product' permission.
    """
    try:
        if skip < 0:
            raise ValueError("Skip parameter cannot be negative")
        if limit < 1 or limit > 1000:
            raise ValueError("Limit must be between 1 and 1000")
            
        user_id = request.state.user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
            
        products = ProductService.get_products(db=db, skip=skip, limit=limit, user_id=user_id)
        return StandardResponse.success(
            data=products,
            message="Products retrieved successfully"
        )
    except ValueError as e:
        logger.error(f"Validation error getting products: {str(e)}")
        return JSONResponse(
            status_code=400,
            content=StandardResponse.error(str(e))
        )
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=StandardResponse.error(f"Error getting products: {str(e)}")
        )

@router.put("/{product_id}", response_model=Product)
@check_permissions(["update_product"])
def update_product(
    request: Request,
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a product. Requires 'update_product' permission.
    """
    try:
        user_id = request.state.user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
            
        updated_product = ProductService.update_product(
            db=db,
            product_id=product_id,
            product=product,
            user_id=user_id
        )
        return StandardResponse.success(
            data=updated_product,
            message="Product updated successfully"
        )
    except ValueError as e:
        logger.error(f"Validation error updating product: {str(e)}")
        return JSONResponse(
            status_code=400,
            content=StandardResponse.error(str(e))
        )
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=StandardResponse.error(f"Error updating product: {str(e)}")
        )

@router.delete("/{product_id}")
@check_permissions(["delete_product"])
def delete_product(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a product. Requires 'delete_product' permission.
    """
    try:
        user_id = request.state.user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
            
        success = ProductService.delete_product(db=db, product_id=product_id, user_id=user_id)
        return StandardResponse.success(
            message="Product deleted successfully"
        )
    except ValueError as e:
        logger.error(f"Validation error deleting product: {str(e)}")
        return JSONResponse(
            status_code=400,
            content=StandardResponse.error(str(e))
        )
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=StandardResponse.error(f"Error deleting product: {str(e)}")
        )

@router.post("/create-tables")
@check_permissions(["manage_database"])
def create_product_tables(db: Session = Depends(get_db)):
    """
    Create product table. Requires 'manage_database' permission.
    """
    try:
        ProductService.create_tables()
        return StandardResponse.success(message="Product tables created successfully")
    except Exception as e:
        logger.error(f"Error creating product tables: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=StandardResponse.error(f"Error creating product tables: {str(e)}")
        ) 