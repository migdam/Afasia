"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .core.config import settings
from .core.logging import configure_logging, logger
from .db.database import init_db
from .api.v1.endpoints import auth, therapy, users, admin
import os

# Configure logging
configure_logging()

# Create FastAPI app
app = FastAPI(
    title="Aphasia Speech Therapy API",
    description="API for speech therapy application for aphasia patients",
    version="1.0.0",
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Mount static files
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# Health check endpoints
@app.get("/health")
def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "aphasia-therapy-api"}


@app.get("/health/detailed")
def detailed_health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": "aphasia-therapy-api",
        "version": "1.0.0",
        "debug": settings.DEBUG,
        "database": "connected",
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(therapy.router, prefix="/api/v1/therapy", tags=["Therapy"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting Aphasia Speech Therapy API")
    init_db()
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Aphasia Speech Therapy API")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
