from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app.modules.common.config.database import get_db
from app.modules.users.schemas.user import User, UserCreate
from app.modules.users.services import user_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return user_service.create_user(db=db, user=user)
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error in create_user endpoint: {error_message}")
        
        if "Database table" in error_message:
            raise HTTPException(status_code=500, detail="Database table error. Please check if the database is properly initialized.")
        elif "already registered" in error_message or "already exists" in error_message:
            raise HTTPException(status_code=400, detail=error_message)
        else:
            raise HTTPException(status_code=500, detail=f"Error creating user: {error_message}")

@router.get("/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user_service.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user 