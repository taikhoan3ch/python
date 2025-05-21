from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the absolute path to the static directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Import and include routers
from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    try:
        index_path = os.path.join(STATIC_DIR, "index.html")
        if not os.path.exists(index_path):
            raise HTTPException(status_code=404, detail="index.html not found")
        return FileResponse(index_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/{path:path}")
async def serve_static(path: str):
    try:
        if path.endswith(".html"):
            file_path = os.path.join(STATIC_DIR, path)
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"File {path} not found")
            return FileResponse(file_path)
        return {"message": "Not Found"}, 404
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 