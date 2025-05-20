from sqlalchemy.orm import Session
from app.modules.users.models.user import User
from app.modules.users.schemas.user import UserCreate
from app.modules.common.utils.security import get_password_hash
import logging
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

logger = logging.getLogger(__name__)

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    try:
        # Check if table exists
        try:
            db.query(User).first()
        except Exception as e:
            logger.error(f"Database table error: {str(e)}")
            raise Exception("Database table 'users' does not exist or is not accessible")

        # Check for existing user
        existing_user = get_user_by_email(db, email=user.email)
        if existing_user:
            logger.warning(f"Attempt to create user with existing email: {user.email}")
            raise Exception("Email already registered")

        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"Successfully created user: {user.email}")
            return db_user
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error: {str(e)}")
            raise Exception("Username or email already exists")
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise Exception("Database error occurred while creating user")
            
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise Exception(f"Failed to create user: {str(e)}") 