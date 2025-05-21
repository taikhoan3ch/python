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

@router.post("/", response_model=Product)
@check_permissions(["create_product"])
def create_product(
    request: Request,
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new product. Requires 'create_product' permission.
    """
    logger.info("Starting product creation process")
    try:
        user_id = request.state.user.get("id")
        logger.debug(f"Retrieved user_id: {user_id}")
        
        if not user_id:
            logger.warning("Authentication failed - no user_id found")
            raise HTTPException(status_code=401, detail="User not authenticated")
            
        logger.info(f"Creating product for user_id: {user_id}")
        created_product = ProductService.create_product(db=db, product=product, user_id=user_id)
        logger.info(f"Successfully created product with ID: {created_product.id}")
        return created_product
   
    except ValueError as e:
        logger.error(f"Validation error creating product: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.exception("Unhandled error while creating product")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

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
    logger.info(f"Starting get_products request with skip={skip}, limit={limit}")
    try:
        if skip < 0:
            logger.warning(f"Invalid skip parameter: {skip}")
            raise ValueError("Skip parameter cannot be negative")
        if limit < 1 or limit > 1000:
            logger.warning(f"Invalid limit parameter: {limit}")
            raise ValueError("Limit must be between 1 and 1000")
            
        user_id = request.state.user.get("id")
        logger.debug(f"Retrieved user_id: {user_id}")
        
        if not user_id:
            logger.warning("Authentication failed - no user_id found")
            raise HTTPException(status_code=401, detail="User not authenticated")
            
        logger.info(f"Fetching products for user_id: {user_id}")
        products = ProductService.get_products(db=db, skip=skip, limit=limit, user_id=user_id)
        logger.info(f"Successfully retrieved {len(products)} products")
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
    logger.info(f"Starting product update process for product_id: {product_id}")
    try:
        user_id = request.state.user.get("id")
        logger.debug(f"Retrieved user_id: {user_id}")
        
        if not user_id:
            logger.warning("Authentication failed - no user_id found")
            raise HTTPException(status_code=401, detail="User not authenticated")
            
        logger.info(f"Updating product {product_id} for user_id: {user_id}")
        updated_product = ProductService.update_product(
            db=db,
            product_id=product_id,
            product=product,
            user_id=user_id
        )
        logger.info(f"Successfully updated product {product_id}")
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
    logger.info(f"Starting product deletion process for product_id: {product_id}")
    try:
        user_id = request.state.user.get("id")
        logger.debug(f"Retrieved user_id: {user_id}")
        
        if not user_id:
            logger.warning("Authentication failed - no user_id found")
            raise HTTPException(status_code=401, detail="User not authenticated")
            
        logger.info(f"Deleting product {product_id} for user_id: {user_id}")
        success = ProductService.delete_product(db=db, product_id=product_id, user_id=user_id)
        logger.info(f"Successfully deleted product {product_id}")
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
    logger.info("Starting product tables creation process")
    try:
        logger.debug("Calling ProductService.create_tables()")
        ProductService.create_tables()
        logger.info("Successfully created product tables")
        return StandardResponse.success(message="Product tables created successfully")
    except Exception as e:
        logger.error(f"Error creating product tables: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=StandardResponse.error(f"Error creating product tables: {str(e)}")
        ) 