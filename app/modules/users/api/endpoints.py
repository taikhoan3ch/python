from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
import logging
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.modules.common.config.database import get_db
from app.modules.users.schemas.user import User, UserCreate, UserUpdate
from app.modules.users.services import user_service
from app.modules.common.utils.response import StandardResponse
from app.modules.common.middleware.auth_middleware import check_permissions
from app.modules.common.utils.jwt import create_access_token
from app.modules.common.utils.security import verify_password

logger = logging.getLogger(__name__)
router = APIRouter()

class LoginData(BaseModel):
    email: str
    password: str

@router.post("/")
@check_permissions(["create_user"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user. Requires 'create_user' permission.
    """
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
@check_permissions(["read_user"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all users. Requires 'read_user' permission.
    """
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
@check_permissions(["read_user"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user. Requires 'read_user' permission.
    """
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

@router.put("/{user_id}")
@check_permissions(["update_user"])
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user. Requires 'update_user' permission.
    """
    try:
        updated_user = user_service.update_user(db, user_id=user_id, user=user)
        if updated_user is None:
            return JSONResponse(
                status_code=404,
                content=StandardResponse.error("User not found")
            )
        return StandardResponse.success(
            data=updated_user,
            message="User updated successfully"
        )
    except Exception as e:
        logger.error(f"Error in update_user endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=StandardResponse.error("Error updating user")
        )

@router.delete("/{user_id}")
@check_permissions(["delete_user"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user. Requires 'delete_user' permission.
    """
    try:
        if not user_service.delete_user(db, user_id=user_id):
            return JSONResponse(
                status_code=404,
                content=StandardResponse.error("User not found")
            )
        return StandardResponse.success(
            message="User deleted successfully"
        )
    except Exception as e:
        logger.error(f"Error in delete_user endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=StandardResponse.error("Error deleting user")
        )

@router.post("/login")
def login(login_data: LoginData, db: Session = Depends(get_db)):
    """
    Login user and return JWT token
    """
    try:
        user = user_service.get_user_by_email(db, email=login_data.email)
        if not user:
            return JSONResponse(
                status_code=401,
                content=StandardResponse.error("Invalid email or password")
            )

        if not verify_password(login_data.password, user.hashed_password):
            return JSONResponse(
                status_code=401,
                content=StandardResponse.error("Invalid email or password")
            )

        # Create access token
        access_token = create_access_token(data={"sub": user.email})
        
        # Get user permissions
        permissions = [p.name for p in user.role.permissions] if user.role else []

        return StandardResponse.success(
            data={
                "token": access_token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "permissions": permissions
                }
            },
            message="Login successful"
        )
    except Exception as e:
        logger.error(f"Error in login endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=StandardResponse.error("Error during login")
        )

@router.get("/me")
@check_permissions([])  # No specific permissions required, just valid token
def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Get current user information
    """
    try:
        user = request.state.user
        permissions = [p.name for p in user.role.permissions] if user.role else []
        
        return StandardResponse.success(
            data={
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "permissions": permissions
            },
            message="User information retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error in get_current_user endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=StandardResponse.error("Error retrieving user information")
        ) 