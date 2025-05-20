from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from typing import Optional, Any, Dict
import logging
from app.modules.common.config.settings import settings
from app.modules.users.api.endpoints import router as users_router
import os

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

class StandardResponse:
    @staticmethod
    def success(data: Optional[Any] = None, message: Optional[str] = None) -> Dict:
        return {
            "success": True,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def error(message: str, data: Optional[Any] = None) -> Dict:
        return {
            "success": False,
            "message": message,
            "data": data
        }

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

# Include routers
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])

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