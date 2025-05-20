from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from typing import Optional, Any, Dict
import logging
from app.modules.common.config.settings import settings
from app.modules.users.api.endpoints import router as users_router
from app.modules.common.utils.response import StandardResponse
import os
from app.modules.common.config.database import engine, Base
from app.modules.users.api import user_api
from app.modules.products.api import product_api
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
            status_code=500,
            content=StandardResponse.error("Internal server error")
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
app.include_router(user_api.router)
app.include_router(product_api.router)

@app.get("/")
async def root():
    try:
        return FileResponse("app/static/index.html")
    except Exception as e:
        logger.error(f"Error serving index.html: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=StandardResponse.error("Error serving static file")
        )

@app.get("/api")
async def api_info():
    try:
        return StandardResponse.success(
            data={
                "version": settings.VERSION,
                "docs_url": "/docs",
                "redoc_url": "/redoc"
            },
            message="Welcome to User Info API"
        )
    except Exception as e:
        logger.error(f"Error in api_info: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=StandardResponse.error("Internal server error")
        )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content=StandardResponse.error("Validation error", data=exc.errors())
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=StandardResponse.error("Internal server error")
    ) 