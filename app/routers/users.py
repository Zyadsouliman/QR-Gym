from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from .. import crud, schemas
from ..database import get_db
from ..utils.auth import create_access_token, create_refresh_token, verify_token, get_token_scopes
from ..utils.otp import create_otp, verify_otp
from ..utils.email_sms import send_otp_email, send_otp_sms
from ..config import get_settings
from ..utils.limiter import limiter
import logging

router = APIRouter()
settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "read": "Read access",
        "write": "Write access",
        "admin": "Admin access"
    }
)

@router.post("/signup", response_model=schemas.UserOut)
@limiter.limit(f"{settings.SIGNUP_RATE_LIMIT}/minute")
async def signup(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    client_ip = request.client.host
    logging.info(f"Signup attempt from IP: {client_ip}")
    # Check if username exists
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if phone number exists
    if crud.get_user_by_phone(db, user.phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Create user with hashed password
    db_user = crud.create_user(db, user)
    
    # Generate and send OTP
    otp = create_otp(db, db_user.id)
    send_otp_email(db_user.email, otp.otp_code)
    send_otp_sms(db_user.phone_number, otp.otp_code)
    
    return db_user

@router.post("/verify-otp", response_model=schemas.Token)
@limiter.limit(f"{settings.OTP_MAX_ATTEMPTS}/minute")
async def verify_otp_endpoint(request: Request, otp_data: schemas.OTPVerify, db: Session = Depends(get_db)):
    client_ip = request.client.host
    logging.info(f"OTP verification attempt from IP: {client_ip}")
    user = crud.get_user_by_username(db, otp_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )
    
    if verify_otp(db, user.id, otp_data.otp_code):
        user.is_active = True
        db.commit()
        
        access_token = create_access_token(
            data={"sub": user.username, **get_token_scopes(["read"])},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(
            data={"sub": user.username}
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid credentials"
    )

@router.post("/token", response_model=schemas.Token)
@limiter.limit(f"{settings.LOGIN_RATE_LIMIT}/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    client_ip = request.client.host
    logging.info(f"Login attempt from IP: {client_ip}")
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.username, **get_token_scopes(form_data.scopes)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username}
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=schemas.Token)
@limiter.limit(f"{settings.LOGIN_RATE_LIMIT}/minute")
async def refresh_token(request: Request, refresh_token: str, db: Session = Depends(get_db)):
    client_ip = request.client.host
    logging.info(f"Token refresh attempt from IP: {client_ip}")
    try:
        payload = verify_token(refresh_token, is_refresh=True)
        username = payload.get("sub")
        if not username:
            raise ValueError("Invalid token")
        
        user = crud.get_user_by_username(db, username)
        if not user or not user.is_active:
            raise ValueError("Invalid user")
        
        access_token = create_access_token(
            data={"sub": username, **get_token_scopes()},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        new_refresh_token = create_refresh_token(
            data={"sub": username}
        )
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/gym-id", response_model=schemas.GymIDCreate)
async def create_gym_id_endpoint(
    gym_id: schemas.GymIDCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    payload = verify_token(token)
    if "write" not in payload.get("scopes", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return crud.create_gym_id(db, gym_id)

@router.get("/gym-ids", response_model=List[schemas.GymIDCreate])
async def get_user_gym_ids_endpoint(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    payload = verify_token(token)
    if "read" not in payload.get("scopes", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    username = payload.get("sub")
    user = crud.get_user_by_username(db, username)
    return crud.get_user_gym_ids(db, user.id) 

@router.get("/signup")
async def signup_get():
    return {"detail": "Method GET not allowed, please use POST for signup."}

@router.get("/verify-otp")
async def verify_otp_get():
    return {"detail": "Method GET not allowed, please use POST for OTP verification."}

@router.get("/gym-id")
async def gym_id_get():
    return {"detail": "Method GET not allowed, please use POST for creating gym id."}

@router.get("/token")
async def token_get():
    return {"detail": "GET method not allowed. Please use POST to obtain token."}

