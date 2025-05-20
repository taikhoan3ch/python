from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from app.modules.common.config.database import get_db
from app.modules.users.services.user_service import get_user_by_email
from app.modules.common.utils.jwt import decode_token
from functools import wraps

security = HTTPBearer()

def check_permissions(required_permissions: List[str]):
    """
    Middleware decorator to check if user has required permissions
    Usage:
    @router.get("/products")
    @check_permissions(["read_product"])
    def get_products():
        ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request object from args
            request = next((arg for arg in args if isinstance(arg, Request)), None)
            if not request:
                raise HTTPException(status_code=500, detail="Request object not found")

            # Get database session
            db = next((arg for arg in args if isinstance(arg, Session)), None)
            if not db:
                db = next(get_db())

            try:
                # Get token from header
                auth = await security(request)
                token = auth.credentials
                
                # Decode token to get user email
                payload = decode_token(token)
                user_email = payload.get("sub")
                
                if not user_email:
                    raise HTTPException(status_code=401, detail="Invalid token")

                # Get user from database
                user = get_user_by_email(db, email=user_email)
                if not user:
                    raise HTTPException(status_code=401, detail="User not found")

                # Check if user has role
                if not user.role:
                    raise HTTPException(status_code=403, detail="User has no role assigned")

                # Get user permissions
                user_permissions = [p.name for p in user.role.permissions]

                # Check if user has all required permissions
                missing_permissions = [perm for perm in required_permissions if perm not in user_permissions]
                if missing_permissions:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Missing required permissions: {', '.join(missing_permissions)}"
                    )

                # Add user to request state for use in route handler
                request.state.user = user
                
                return await func(*args, **kwargs)

            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        return wrapper
    return decorator 