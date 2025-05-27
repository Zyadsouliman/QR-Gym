import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import OTP
from ..config import get_settings

settings = get_settings()

def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def create_otp(db: Session, user_id: int) -> OTP:
    """Create a new OTP for a user"""
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRATION_MINUTES)
    
    otp = OTP(
        user_id=user_id,
        otp_code=otp_code,
        expires_at=expires_at
    )
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp

def verify_otp(db: Session, user_id: int, otp_code: str) -> bool:
    """Verify if the OTP is valid"""
    otp = db.query(OTP).filter(
        OTP.user_id == user_id,
        OTP.otp_code == otp_code,
        OTP.is_used == False,
        OTP.expires_at > datetime.utcnow()
    ).first()
    
    if otp:
        otp.is_used = True
        db.commit()
        return True
    return False 