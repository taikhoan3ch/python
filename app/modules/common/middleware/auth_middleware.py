from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional, Literal
from app.modules.common.config.database import get_db
from app.modules.users.services.user_service import get_user_by_email
from app.modules.common.utils.jwt import decode_token
from functools import wraps, lru_cache
from datetime import datetime, timedelta

security = HTTPBearer()

@lru_cache(maxsize=1000)
def get_cached_user_permissions(user_id: int, cache_time: datetime) -> List[str]:
    """
    Cache user permissions for 5 minutes to reduce database queries
    """
    return []

def check_permissions(
    required_permissions: List[str],
    logic: Literal["AND", "OR"] = "AND",
    cache_timeout: int = 300  # 5 minutes in seconds
):
    """
    Middleware decorator to check if user has required permissions
    Args:
        required_permissions: List of required permissions
        logic: "AND" or "OR" to specify how permissions should be checked
        cache_timeout: Time in seconds to cache user permissions
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

            # Get database session using dependency injection
            db = next((arg for arg in args if isinstance(arg, Session)), None)
            if not db:
                db = next(get_db())

            try:
                # Get token from header
                try:
                    auth = await security(request)
                    token = auth.credentials
                except Exception as e:
                    raise HTTPException(status_code=401, detail="Invalid authentication credentials")

                # Decode token to get user email
                try:
                    payload = decode_token(token)
                except Exception as e:
                    raise HTTPException(status_code=401, detail="Invalid or expired token")

                user_email = payload.get("sub")
                if not user_email:
                    raise HTTPException(status_code=401, detail="Invalid token format")

                # Get user from database
                user = get_user_by_email(db, email=user_email)
                if not user:
                    raise HTTPException(status_code=401, detail="User not found")

                # Check if user has role
                if not user.role:
                    raise HTTPException(status_code=403, detail="User has no role assigned")

                # Try to get cached permissions first
                cache_time = datetime.now().replace(second=0, microsecond=0)
                user_permissions = get_cached_user_permissions(user.id, cache_time)

                # If not in cache, get from database
                if not user_permissions:
                    user_permissions = [p.name for p in user.role.permissions]
                    # Update cache
                    get_cached_user_permissions.cache_clear()  # Clear old cache
                    get_cached_user_permissions(user.id, cache_time)  # Add new cache

                # Check permissions based on logic
                if logic == "AND":
                    missing_permissions = [perm for perm in required_permissions if perm not in user_permissions]
                    if missing_permissions:
                        raise HTTPException(
                            status_code=403,
                            detail=f"Missing required permissions: {', '.join(missing_permissions)}"
                        )
                elif logic == "OR":
                    if not any(perm in user_permissions for perm in required_permissions):
                        raise HTTPException(
                            status_code=403,
                            detail=f"Missing all required permissions: {', '.join(required_permissions)}"
                        )

                # Add minimal user info to request state
                request.state.user = {
                    "id": user.id,
                    "email": user.email,
                    "permissions": user_permissions
                }
                
                return await func(*args, **kwargs)

            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

        return wrapper
    return decorator 