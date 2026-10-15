"""Main FastAPI application."""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.logging import configure_logging, logger
from .db.database import init_db
from .retention import clean_up, clean_up_daily
from .api.v1.endpoints import auth, therapy, users, admin
import os

# Configure logging
configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Set up the database on startup, and the daily recording clean-up if
    RECORDING_RETENTION_DAYS is set; log the shutdown."""
    logger.info("Starting Aphasia Speech Therapy API")
    init_db()
    logger.info("Database initialized")
    daily = None
    if settings.RECORDING_RETENTION_DAYS > 0:
        await clean_up()  # before the first request
        daily = asyncio.create_task(clean_up_daily())
    yield
    if daily:
        daily.cancel()
    logger.info("Shutting down Aphasia Speech Therapy API")


# Create FastAPI app
app = FastAPI(
    lifespan=lifespan,
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

# Create upload directory. It is never served directly: recordings are
# health data, so they go out only through the owner-checked
# GET /api/v1/users/audio/{id}.
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
