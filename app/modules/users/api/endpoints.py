from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging
from fastapi.responses import JSONResponse

from app.modules.common.config.database import get_db
from app.modules.users.schemas.user import User, UserCreate
from app.modules.users.services import user_service
from app.modules.common.utils.response import StandardResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        created_user = user_service.create_user(db=db, user=user)
        return StandardResponse.success(
            data=created_user,
            message="User created successfully"
        )
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error in create_user endpoint: {error_message}")
        
        if "Database table" in error_message:
            return JSONResponse(
                status_code=500,
                content=StandardResponse.error("Database table error. Please check if the database is properly initialized.")
            )
        elif "already registered" in error_message or "already exists" in error_message:
            return JSONResponse(
                status_code=400,
                content=StandardResponse.error(error_message)
            )
        else:
            return JSONResponse(
                status_code=500,
                content=StandardResponse.error(f"Error creating user: {error_message}")
            )

@router.get("/")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        users = user_service.get_users(db, skip=skip, limit=limit)
        return StandardResponse.success(
            data=users,
            message="Users retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error in read_users endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=StandardResponse.error("Error retrieving users")
        )

@router.get("/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    try:
        db_user = user_service.get_user(db, user_id=user_id)
        if db_user is None:
            return JSONResponse(
                status_code=404,
                content=StandardResponse.error("User not found")
            )
        return StandardResponse.success(
            data=db_user,
            message="User retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error in read_user endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=StandardResponse.error("Error retrieving user")
        ) 