from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from typing import Optional, Any, Dict
import logging
from app.modules.common.config.settings import settings
from app.modules.users.api.endpoints import router as users_router
import os
from app.modules.common.config.database import engine, Base
from app.modules.products.api.endpoints import router as products_router
from app.modules.users.services.role_service import RoleService
from app.modules.common.config.database import SessionLocal

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Add HTTPS redirect middleware
@app.middleware("http")
async def https_redirect_middleware(request: Request, call_next):
    try:
        # Check if the request is coming from Railway's proxy
        forwarded_proto = request.headers.get("x-forwarded-proto", "")
        if forwarded_proto == "https":
            return await call_next(request)
        
        # If not HTTPS, redirect
        url = str(request.url).replace("http://", "https://", 1)
        return RedirectResponse(url=url, status_code=301)
    except Exception as e:
        logger.error(f"Middleware error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"Middleware error: {str(e)}"}
        )

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize roles and permissions
def init_roles():
    db = SessionLocal()
    try:
        RoleService.initialize_default_roles_and_permissions(db)
    finally:
        db.close()

# Initialize roles on startup
@app.on_event("startup")
async def startup_event():
    init_roles()

# Include routers
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(products_router, prefix=f"{settings.API_V1_STR}/products", tags=["products"])

@app.get("/")
async def root():
    try:
        return FileResponse("app/static/index.html")
    except Exception as e:
        logger.error(f"Error serving index.html: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"Error serving static file: {str(e)}"}
        )

@app.get("/api")
async def api_info():
    try:
        return {"success": True, "message": "API is running", "data": {"version": "1.0.0"}}
    except Exception as e:
        logger.error(f"Error in api_info: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"Error in api_info: {str(e)}"}
        )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "message": "Validation error", "data": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": f"Unexpected error: {str(exc)}"}
    ) 