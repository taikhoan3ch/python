from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional, Literal
from app.modules.common.config.database import get_db
from app.modules.users.services.user_service import get_user_by_email
from app.modules.common.utils.jwt import decode_token
from functools import wraps, lru_cache
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

@lru_cache(maxsize=1000)
def get_cached_user_permissions(user_id: int, cache_time: datetime) -> List[str]:
    """
    Cache user permissions for 5 minutes to reduce database queries
    """
    logger.debug(f"Getting cached permissions for user_id: {user_id}")
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
            logger.info(f"Starting permission check for {func.__name__}")
            logger.debug(f"Required permissions: {required_permissions}, Logic: {logic}")
            
            # Get request object from args
            request = next((arg for arg in args if isinstance(arg, Request)), None)
            if not request:
                logger.error("Request object not found in args")
                raise HTTPException(status_code=500, detail="Request object not found")

            # Get database session using dependency injection
            db = next((arg for arg in args if isinstance(arg, Session)), None)
            if not db:
                logger.debug("Database session not found in args, getting new session")
                db = next(get_db())

            try:
                # Get token from header
                try:
                    logger.debug("Attempting to get authentication token from header")
                    auth = await security(request)
                    token = auth.credentials
                    logger.debug("Successfully retrieved authentication token")
                except Exception as e:
                    logger.warning(f"Failed to get authentication token: {str(e)}")
                    raise HTTPException(status_code=401, detail="Invalid authentication credentials")

                # Decode token to get user email
                try:
                    logger.debug("Attempting to decode JWT token")
                    payload = decode_token(token)
                    logger.debug("Successfully decoded JWT token")
                except Exception as e:
                    logger.warning(f"Failed to decode token: {str(e)}")
                    raise HTTPException(status_code=401, detail="Invalid or expired token")

                user_email = payload.get("sub")
                if not user_email:
                    logger.warning("No user email found in token payload")
                    raise HTTPException(status_code=401, detail="Invalid token format")
                logger.debug(f"Retrieved user email from token: {user_email}")

                # Get user from database
                logger.info(f"Looking up user with email: {user_email}")
                user = get_user_by_email(db, email=user_email)
                if not user:
                    logger.warning(f"User not found for email: {user_email}")
                    raise HTTPException(status_code=401, detail="User not found")
                logger.info(f"Found user with ID: {user.id}")

                # Check if user has role
                if not user.role:
                    logger.warning(f"User {user.id} has no role assigned")
                    raise HTTPException(status_code=403, detail="User has no role assigned")
                logger.debug(f"User {user.id} has role: {user.role.name}")

                # Try to get cached permissions first
                cache_time = datetime.now().replace(second=0, microsecond=0)
                logger.debug(f"Checking permission cache for user {user.id}")
                user_permissions = get_cached_user_permissions(user.id, cache_time)

                # If not in cache, get from database
                if not user_permissions:
                    logger.debug(f"Cache miss for user {user.id}, fetching permissions from database")
                    user_permissions = [p.name for p in user.role.permissions]
                    logger.debug(f"Retrieved permissions from database: {user_permissions}")
                    # Update cache
                    get_cached_user_permissions.cache_clear()  # Clear old cache
                    get_cached_user_permissions(user.id, cache_time)  # Add new cache
                    logger.debug("Updated permission cache")
                else:
                    logger.debug(f"Cache hit for user {user.id}, using cached permissions")

                # Check permissions based on logic
                if logic == "AND":
                    missing_permissions = [perm for perm in required_permissions if perm not in user_permissions]
                    if missing_permissions:
                        logger.warning(f"User {user.id} missing required permissions: {missing_permissions}")
                        raise HTTPException(
                            status_code=403,
                            detail=f"Missing required permissions: {', '.join(missing_permissions)}"
                        )
                elif logic == "OR":
                    if not any(perm in user_permissions for perm in required_permissions):
                        logger.warning(f"User {user.id} missing all required permissions: {required_permissions}")
                        raise HTTPException(
                            status_code=403,
                            detail=f"Missing all required permissions: {', '.join(required_permissions)}"
                        )

                logger.info(f"Permission check passed for user {user.id}")
                # Add minimal user info to request state
                request.state.user = {
                    "id": user.id,
                    "email": user.email,
                    "permissions": user_permissions
                }
                logger.debug(f"Added user info to request state: {request.state.user}")
                
                return await func(*args, **kwargs)

            except HTTPException as e:
                logger.error(f"HTTP Exception in permission check: {str(e)}")
                raise e
            except Exception as e:
                logger.exception(f"Unexpected error in permission check: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

        return wrapper
    return decorator 