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
        query = db.query(Product)
        if user_id:
            query = query.filter(Product.created_by == user_id)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_product(
        db: Session,
        product_id: int,
        product: ProductUpdate,
        user_id: int
    ) -> Optional[Product]:
        db_product = db.query(Product).filter(
            Product.id == product_id,
            Product.created_by == user_id
        ).first()
        
        if not db_product:
            return None
            
        update_data = product.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
            
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def delete_product(db: Session, product_id: int, user_id: int) -> bool:
        db_product = db.query(Product).filter(
            Product.id == product_id,
            Product.created_by == user_id
        ).first()
        
        if not db_product:
            return False
            
        db.delete(db_product)
        db.commit()
        return True

    @staticmethod
    def create_tables():
        """Create product table if it doesn't exist"""
        Base.metadata.create_all(bind=engine, tables=[Product.__table__]) 