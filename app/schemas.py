from pydantic import BaseModel, EmailStr, Field, model_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class GymIDType(str, Enum):
    normal = "normal"
    premium = "premium"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    # phone_number: str = Field(pattern=r'^(\+?\d{1,3}|0)\d{9,15}$')
    date_of_birth: datetime


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)

    @model_validator(mode='after')
    def passwords_match(cls, model):
        if model.password != model.confirm_password:
            raise ValueError("Passwords do not match")
        return model

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OTPVerify(BaseModel):
    username: str
    otp_code: str

class ResendOTP(BaseModel):
    email: str

class GymIDBase(BaseModel):
    id_type: str

class GymIDCreate(GymIDBase):
    pass

class GymIDOut(GymIDBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ExerciseBase(BaseModel):
    name: str
    muscle_group: str
    media_url: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseOut(ExerciseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WorkoutPlanBase(BaseModel):
    plan_name: str
    exercise_ids: List[int]

class WorkoutPlanCreate(WorkoutPlanBase):
    pass

class WorkoutPlanOut(WorkoutPlanBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    exercises: List[ExerciseOut]

    class Config:
        from_attributes = True

class NutritionPlanBase(BaseModel):
    plan_name: str

class NutritionPlanCreate(NutritionPlanBase):
    pass

class NutritionPlanOut(NutritionPlanBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RefreshToken(BaseModel):
    refresh_token: str

class GenerateIDsRequest(BaseModel):
    type: GymIDType

class GenerateIDsResponse(BaseModel):
    message: str
    ids: List[str]

class GymAccessIDBase(BaseModel):
    code: str
    type: GymIDType
    is_used: bool = False

class GymAccessIDCreate(GymAccessIDBase):
    pass

class GymAccessIDOut(GymAccessIDBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VerifyIDRequest(BaseModel):
    access_id: str = Field(..., pattern=r'^(QRG|PREM)\d{8}$')

class VerifyIDResponse(BaseModel):
    is_valid: bool
    message: str
    id_type: str