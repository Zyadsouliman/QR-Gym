from fastapi import FastAPI, Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.responses import Response, JSONResponse
from .routers import users
from .database import engine
from . import models
from .config import get_settings
from .utils.limiter import limiter
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create database tables
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.error(f"Failed to create database tables: {str(e)}")
    # Don't raise the exception, allow the app to start even if tables exist

# Configure OAuth2 security scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/users/token")

app = FastAPI(
    title="Gym QR Code Backend System",
    description="Backend API for Gym QR Code Management System",
    version="1.0.0",
    docs_url="/docs",  # Enable docs at root level
    redoc_url="/redoc",  # Enable redoc at root level
    openapi_url="/openapi.json",  # Enable OpenAPI schema at root level
    openapi_tags=[
        {
            "name": "users",
            "description": "User management operations",
        }
    ],
    components={
        "securitySchemes": {
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": f"{settings.API_V1_STR}/users/token",
                        "scopes": {
                            "read": "Read access",
                            "write": "Write access",
                            "admin": "Admin access"
                        }
                    }
                }
            }
        }
    },
    security=[{"OAuth2PasswordBearer": []}]
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware with more permissive settings for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # More permissive for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simplified middleware configuration for serverless
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="gymqr_session",
    max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    same_site="lax",  # More permissive for development
    https_only=False,  # More permissive for development
)

# Include routers with API version prefix
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])

@app.get("/")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def read_root(request: Request):
    try:
        client_ip = request.client.host
        logger.info(f"Root endpoint accessed from IP: {client_ip}")
        return {
            "message": "Welcome to the Gym QR Code Backend System",
            "version": "1.0.0",
            "docs_url": "/docs",
            "api_url": settings.API_V1_STR
        }
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)  # No content response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error handler caught: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

app = app