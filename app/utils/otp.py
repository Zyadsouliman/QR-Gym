import random
import string
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from ..models import OTP, User
from ..config import get_settings
from ..utils.email_sms import send_otp_email

settings = get_settings()

def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def create_otp(db: Session, username: str) -> OTP:
    """Create a new OTP for a user"""
    # Get user email from database
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise ValueError("User not found")
        
    otp_code = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRATION_MINUTES)
    
    otp = OTP(
        username=username,
        otp_code=otp_code,
        expires_at=expires_at
    )
    db.add(otp)
    db.commit()
    db.refresh(otp)
    
    # Send OTP via email
    send_otp_email(user.email, otp_code)
    
    return otp

def verify_otp(db: Session, username: str, otp_code: str) -> bool:
    """Verify if the OTP is valid"""
    otp = db.query(OTP).filter(
        OTP.username == username,
        OTP.otp_code == otp_code,
        OTP.is_used == False,
        OTP.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if otp:
        otp.is_used = True
        db.commit()
        return True
    return False 