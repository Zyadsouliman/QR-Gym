from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    GenerateIDsRequest, 
    GenerateIDsResponse, 
    VerifyIDRequest, 
    VerifyIDResponse,
    TokenData
)
from app.utils.id_generator import generate_unique_ids
from app.utils.auth import get_current_user
import logging

router = APIRouter(
    prefix="/gym-ids",
    tags=["gym-ids"]
)

@router.post("/generate", response_model=GenerateIDsResponse)
async def generate_ids(
    request: GenerateIDsRequest,
    db: Session = Depends(get_db)
):
    try:
        logging.info(f"Generating {request.type.value} IDs")
        generated_ids = generate_unique_ids(db, request.type.value)
        logging.info(f"Successfully generated IDs: {generated_ids}")
        return GenerateIDsResponse(
            message=f"10 {request.type.value} IDs generated successfully",
            ids=generated_ids
        )
    except Exception as e:
        logging.error(f"Error generating IDs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate IDs: {str(e)}"
        )

@router.post("/verify", response_model=VerifyIDResponse)
async def verify_id(
    request: VerifyIDRequest,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Check if the ID exists in the database
        # TODO: Replace this with your actual database query
        # For now, we'll just check the format
        if request.access_id.startswith("QRG"):
            return VerifyIDResponse(
                is_valid=True,
                message="Regular access ID verified successfully",
                id_type="regular"
            )
        elif request.access_id.startswith("PREM"):
            return VerifyIDResponse(
                is_valid=True,
                message="Premium access ID verified successfully",
                id_type="premium"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ID format"
            )
    except Exception as e:
        logging.error(f"Error verifying ID: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify ID: {str(e)}"
        ) 