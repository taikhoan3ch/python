from sqlalchemy.orm import Session
from app.modules.products.models.product import Product
from app.modules.products.schemas.product import ProductCreate, ProductUpdate
from typing import List, Optional
from app.modules.common.config.database import Base, engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class ProductService:
    @staticmethod
    def create_product(db: Session, product: ProductCreate, user_id: int) -> Product:
        try:
            # Validate user exists
            from app.modules.users.models.user import User
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User with ID {user_id} does not exist")

            # Create product
            db_product = Product(
                **product.model_dump(),
                created_by=user_id
            )
            db.add(db_product)
            db.commit()
            db.refresh(db_product)
            return db_product
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error while creating product: {str(e)}")
            raise ValueError("A product with this name already exists")
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while creating product: {str(e)}")
            raise Exception("Database error occurred while creating product")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error while creating product: {str(e)}")
            raise Exception(f"Failed to create product: {str(e)}")

    @staticmethod
    def get_product(db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def get_products(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None
    ) -> List[Product]:
        try:
            query = db.query(Product)
            if user_id:
                # Validate user exists
                from app.modules.users.models.user import User
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    raise ValueError(f"User with ID {user_id} does not exist")
                query = query.filter(Product.created_by == user_id)
            return query.offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error while getting products: {str(e)}")
            raise Exception("Database error occurred while retrieving products")
        except Exception as e:
            logger.error(f"Unexpected error while getting products: {str(e)}")
            raise Exception(f"Failed to get products: {str(e)}")

    @staticmethod
    def update_product(
        db: Session,
        product_id: int,
        product: ProductUpdate,
        user_id: int
    ) -> Optional[Product]:
        try:
            # Validate user exists
            from app.modules.users.models.user import User
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User with ID {user_id} does not exist")

            # Use with_for_update() to handle concurrent updates
            db_product = db.query(Product).filter(
                Product.id == product_id,
                Product.created_by == user_id
            ).with_for_update().first()
            
            if not db_product:
                raise ValueError(f"Product with ID {product_id} not found or you don't have permission to update it")
                
            update_data = product.model_dump(exclude_unset=True)
            
            # Validate stock updates
            if 'stock' in update_data and update_data['stock'] is not None:
                if update_data['stock'] < 0:
                    raise ValueError("Stock cannot be negative")
                if update_data['stock'] > 1000000:
                    raise ValueError("Stock cannot exceed 1,000,000")
            
            # Validate price updates
            if 'price' in update_data and update_data['price'] is not None:
                if update_data['price'] <= 0:
                    raise ValueError("Price must be greater than 0")
                if update_data['price'] > 1000000:
                    raise ValueError("Price cannot exceed 1,000,000")
            
            for field, value in update_data.items():
                setattr(db_product, field, value)
                
            db.commit()
            db.refresh(db_product)
            return db_product
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error while updating product: {str(e)}")
            raise ValueError("A product with this name already exists")
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while updating product: {str(e)}")
            raise Exception("Database error occurred while updating product")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error while updating product: {str(e)}")
            raise Exception(f"Failed to update product: {str(e)}")

    @staticmethod
    def delete_product(db: Session, product_id: int, user_id: int) -> bool:
        try:
            # Validate user exists
            from app.modules.users.models.user import User
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User with ID {user_id} does not exist")

            # Use with_for_update() to handle concurrent deletes
            db_product = db.query(Product).filter(
                Product.id == product_id,
                Product.created_by == user_id
            ).with_for_update().first()
            
            if not db_product:
                raise ValueError(f"Product with ID {product_id} not found or you don't have permission to delete it")
                
            db.delete(db_product)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while deleting product: {str(e)}")
            raise Exception("Database error occurred while deleting product")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error while deleting product: {str(e)}")
            raise Exception(f"Failed to delete product: {str(e)}")

    @staticmethod
    def create_tables():
        """Create product table if it doesn't exist"""
        Base.metadata.create_all(bind=engine, tables=[Product.__table__]) 