from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
import logging
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.modules.common.config.database import get_db
from app.modules.users.schemas.user import User, UserCreate, UserUpdate, UserResponse
from app.modules.users.services import user_service
from app.modules.users.services.role_service import RoleService
from app.modules.common.utils.response import StandardResponse
from app.modules.common.middleware.auth_middleware import check_permissions
from app.modules.common.utils.jwt import create_access_token
from app.modules.common.utils.security import verify_password
from app.modules.common.database import get_current_user
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from app.modules.common.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

class LoginData(BaseModel):
    email: str
    password: str

@router.post("/", response_model=UserResponse)
@check_permissions(["create_user"])
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user. Requires 'create_user' permission.
    """
    try:
        db_user = user_service.create_user(db=db, user=user)
        return {"success": True, "data": db_user}
    except ValueError as error_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    except Exception as error_message:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {error_message}"
        )

@router.get("/", response_model=List[UserResponse])
@check_permissions(["read_user"])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all users. Requires 'read_user' permission.
    """
    try:
        users = user_service.get_users(db, skip=skip, limit=limit)
        return {"success": True, "data": users}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )

@router.get("/me", response_model=UserResponse)
@check_permissions([])  # No specific permissions required, just valid token
async def get_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    """
    try:
        return {"success": True, "data": current_user}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in get_current_user endpoint: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserResponse)
@check_permissions(["read_user"])
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific user. Requires 'read_user' permission.
    """
    try:
        user = user_service.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"success": True, "data": user}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user"
        )

@router.put("/{user_id}", response_model=UserResponse)
@check_permissions(["update_user"])
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a user. Requires 'update_user' permission.
    """
    try:
        updated_user = user_service.update_user(db, user_id=user_id, user=user)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"success": True, "data": updated_user}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user"
        )

@router.delete("/{user_id}")
@check_permissions(["delete_user"])
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a user. Requires 'delete_user' permission.
    """
    try:
        if not user_service.delete_user(db, user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"success": True, "message": "User deleted successfully"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        )

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login user and return JWT token
    """
    try:
        user = user_service.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        )

@router.post("/create-tables")
@check_permissions(["manage_tables"])
async def create_user_tables(db: Session = Depends(get_db)):
    """
    Create user table. Requires 'manage_tables' permission.
    """
    try:
        user_service.create_tables()
        return {"success": True, "message": "User tables created successfully"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create database tables"
        )

@router.post("/drop-tables")
@check_permissions(["manage_tables"])
async def drop_user_tables(db: Session = Depends(get_db)):
    """
    Drop all database tables. Requires 'manage_tables' permission (admin only).
    """
    try:
        from app.modules.common.config.database import Base, engine
        Base.metadata.drop_all(bind=engine)
        return {"success": True, "message": "User tables dropped successfully"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to drop database tables"
        )

@router.post("/create-role-tables")
@check_permissions(["manage_roles"])
async def create_role_tables(db: Session = Depends(get_db)):
    """
    Create role and permission tables. Requires 'manage_roles' permission.
    """
    try:
        RoleService.create_tables()
        return {"success": True, "message": "Role tables created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating role tables: {str(e)}"
        )

@router.post("/create-user-tables")
@check_permissions(["manage_roles"])
async def create_user_tables(db: Session = Depends(get_db)):
    """
    Create user table. Requires 'manage_roles' permission.
    """
    try:
        user_service.create_tables()
        return {"success": True, "message": "User tables created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user tables: {str(e)}"
        ) 