from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class GymIDType(str, Enum):
    STANDARD = "standard"
    PREMIUM = "premium"

class UserBase(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    phone_number: str = Field(pattern=r'^\+?1?\d{9,15}$')
    date_of_birth: datetime

class UserCreate(UserBase):
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)

    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

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