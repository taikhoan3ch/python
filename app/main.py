from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
import logging
from app.modules.common.config.settings import settings
from app.modules.users.api.endpoints import router as users_router

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

# Add HTTPS redirect middleware
@app.middleware("http")
async def https_redirect_middleware(request: Request, call_next):
    # Check if the request is coming from Railway's proxy
    forwarded_proto = request.headers.get("x-forwarded-proto", "")
    if forwarded_proto == "https":
        return await call_next(request)
    
    # If not HTTPS, redirect
    url = str(request.url).replace("http://", "https://", 1)
    return RedirectResponse(url=url, status_code=301)

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
    return {
        "message": "Welcome to User Info API",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    ) 