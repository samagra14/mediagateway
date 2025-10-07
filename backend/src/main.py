"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pathlib import Path

from .config import get_settings
from .db.database import init_db
from .api.routes import router

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="MediaRouter",
    description="Open Source Video Generation Gateway",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Serve video files
storage_path = Path(settings.storage_path)
if storage_path.exists():
    app.mount("/videos", StaticFiles(directory=str(storage_path)), name="videos")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("Database initialized")
    print(f"Server running on http://{settings.host}:{settings.port}")


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "MediaRouter API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
