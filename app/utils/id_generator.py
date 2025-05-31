import random
import string
from typing import List
from sqlalchemy.orm import Session
from app.models import GymAccessID
import logging

def generate_gym_id(type: str) -> str:
    """Generate a single gym ID based on type."""
    try:
        prefix = "QRG" if type == "normal" else "PREM"
        # Generate 8 random digits
        digits = ''.join(random.choices(string.digits, k=8))
        return f"{prefix}{digits}"
    except Exception as e:
        logging.error(f"Error generating gym ID: {str(e)}", exc_info=True)
        raise

def generate_unique_ids(db: Session, type: str, count: int = 10) -> List[str]:
    """Generate multiple unique gym IDs and save them to database."""
    try:
        generated_ids = []
        attempts = 0
        max_attempts = count * 3  # Allow some extra attempts for collision resolution
        
        while len(generated_ids) < count and attempts < max_attempts:
            new_id = generate_gym_id(type)
            
            # Check if ID already exists in database
            existing = db.query(GymAccessID).filter(GymAccessID.code == new_id).first()
            if not existing and new_id not in generated_ids:
                # Create new gym ID record
                gym_id = GymAccessID(code=new_id, type=type)
                db.add(gym_id)
                generated_ids.append(new_id)
            
            attempts += 1
        
        if len(generated_ids) < count:
            raise Exception("Failed to generate requested number of unique IDs")
        
        db.commit()
        return generated_ids
    except Exception as e:
        db.rollback()
        logging.error(f"Error in generate_unique_ids: {str(e)}", exc_info=True)
        raise 