from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum, func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # full_name = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    # phone_number = Column(String(20), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    gym_ids = relationship("GymAccessID", back_populates="user")
    workout_plans = relationship("WorkoutPlan", back_populates="user")
    nutrition_plans = relationship("NutritionPlan", back_populates="user")

class GymAccessID(Base):
    __tablename__ = "gym_access_ids"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    code = Column(String(12), unique=True, nullable=False, index=True)
    type = Column(Enum('normal', 'premium', name='gym_id_type'), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="gym_ids")

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    muscle_group = Column(String(255), nullable=False)
    media_url = Column(String(255))
    sets = Column(Integer)
    reps = Column(Integer)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    plan_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    user = relationship("User", back_populates="workout_plans")
    exercises = relationship("Exercise", secondary="workout_plan_exercises")

class WorkoutPlanExercise(Base):
    __tablename__ = "workout_plan_exercises"

    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id", ondelete="CASCADE"), primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"), primary_key=True)

class NutritionPlan(Base):
    __tablename__ = "nutrition_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    plan_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    user = relationship("User", back_populates="nutrition_plans")

class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), ForeignKey("users.username", ondelete="CASCADE"))
    otp_code = Column(String(6), nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc)) 