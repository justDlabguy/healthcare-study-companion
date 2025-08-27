import os
import logging
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import traceback

from . import models
from .auth import router as auth_router
from .routers import topics as topics_router
from .routers import documents as documents_router
from .routers import flashcards as flashcards_router
from .routers import qa as qa_router
from .routers import study_sessions as study_sessions_router
from .routers import progress as progress_router
from .routers import llm as llm_router
from .routers import search as search_router
from .config import settings
from .database import SessionLocal, engine, Base
from .logging_config import setup_logging, get_logger, LoggingMiddleware, error_tracker
from .monitoring import router as monitoring_router

# Set up structured logging
setup_logging(
    log_level=settings.log_level,
    structured=settings.structured_logging
)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Get structured logger
logger = get_logger(__name__)

app = FastAPI(
    title="Healthcare Study Companion API",
    version="0.1.0",
    description="API for Healthcare Study Companion application using TiDB",
    debug=True
)

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )

# CORS debugging middleware (only in development)
@app.middleware("http")
async def cors_debug_middleware(request: Request, call_next):
    if settings.environment == "development":
        origin = request.headers.get("origin")
        method = request.method
        
        if method == "OPTIONS" or origin:
            logger.debug(f"CORS Request - Method: {method}, Origin: {origin}, Path: {request.url.path}")
            logger.debug(f"Allowed origins: {settings.allowed_origins}")
    
    response = await call_next(request)
    return response

# Configure CORS from settings with enhanced preflight handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token",
        "Cache-Control",
        "Pragma"
    ],
    expose_headers=[
        "Content-Length",
        "Content-Type",
        "X-Total-Count",
        "X-Page-Count"
    ],
    max_age=86400,  # Cache preflight requests for 24 hours
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers
app.include_router(auth_router)
app.include_router(topics_router.router)
app.include_router(documents_router.router)
app.include_router(flashcards_router.router)
app.include_router(qa_router.router)
app.include_router(study_sessions_router.router)
app.include_router(progress_router.router)
app.include_router(llm_router.router)
app.include_router(search_router.router)

# Health check endpoint with database connection test
@app.get("/healthz")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection with SQLAlchemy 2.0 syntax
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        
        # Railway-specific information
        railway_info = {
            "deployment_id": os.getenv("RAILWAY_DEPLOYMENT_ID"),
            "git_commit": os.getenv("RAILWAY_GIT_COMMIT_SHA"),
            "service_name": os.getenv("RAILWAY_SERVICE_NAME"),
        }
        
        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.environment,
            "timestamp": datetime.utcnow().isoformat(),
            "railway": {k: v for k, v in railway_info.items() if v is not None}
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "unhealthy",
                "database": "connection_failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# CORS test endpoint for development
@app.get("/cors-test")
@app.options("/cors-test")
async def cors_test(request: Request):
    """Test endpoint to verify CORS configuration."""
    origin = request.headers.get("origin", "No origin header")
    user_agent = request.headers.get("user-agent", "No user-agent")
    
    return {
        "message": "CORS test successful",
        "origin": origin,
        "user_agent": user_agent,
        "allowed_origins": settings.allowed_origins,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat()
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Healthcare Study Companion API",
        "docs": "/docs",
        "redoc": "/redoc"
    }
