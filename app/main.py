from fastapi import FastAPI, Request, Response
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.responses import Response, JSONResponse
from .routers import users, gym_ids
from .database import engine
from . import models
from .config import get_settings
from .utils.limiter import limiter
import logging

settings = get_settings()

# Create database tables
models.Base.metadata.create_all(bind=engine)

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

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:4200",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:4200",
    "http://100.64.0.2:3000",
    "http://100.64.0.3:3000",
    "http://100.64.0.4:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Add error handler for CORS preflight requests
# @app.exception_handler(Exception)
# async def cors_exception_handler(request: Request, exc: Exception):
#     if request.method == "OPTIONS":
#         return Response(
#             status_code=200,
#             headers={
#                 "Access-Control-Allow-Origin": "*",
#                 "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
#                 "Access-Control-Allow-Headers": "*",
#                 "Access-Control-Max-Age": "600",
#             },
#         )
#     return JSONResponse(
#         status_code=500,
#         content={"detail": str(exc)},
#     )

# Add global OPTIONS handler
@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "600",
        },
    )

# باقي الإعدادات والـ middlewares الأخرى

if settings.FORCE_HTTPS and not settings.DEBUG:
    app.redirect_slashes = True
    app.root_path = "https://" + settings.DOMAIN if hasattr(settings, "DOMAIN") else ""

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Configure with your domain in production
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="gymqr_session",
    max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    same_site=settings.SESSION_COOKIE_SAMESITE,
    https_only=settings.SESSION_COOKIE_SECURE,
)

# Include routers with API version prefix
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(gym_ids.router, prefix=settings.API_V1_STR, tags=["gym-ids"])

@app.get("/")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def read_root(request: Request):
    client_ip = request.client.host
    logging.info(f"Root endpoint accessed from IP: {client_ip}")
    return {
        "message": "Welcome to the Gym QR Code Backend System",
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_url": settings.API_V1_STR
    }

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)  # No content response