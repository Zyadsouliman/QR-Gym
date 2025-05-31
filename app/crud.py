from sqlalchemy.orm import Session
from . import models, schemas
from .utils.auth import get_password_hash, verify_password

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# def get_user_by_phone(db: Session, phone_number: str):
#     return db.query(models.User).filter(models.User.phone_number == phone_number).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        # phone_number=user.phone_number,
        password_hash=hashed_password,
        date_of_birth=user.date_of_birth,
        is_active=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_gym_id(db: Session, gym_id: schemas.GymIDCreate):
    db_gym_id = models.GymID(**gym_id.dict())
    db.add(db_gym_id)
    db.commit()
    db.refresh(db_gym_id)
    return db_gym_id

def get_user_gym_ids(db: Session, user_id: int):
    return db.query(models.GymID).filter(models.GymID.user_id == user_id).all()

def create_exercise(db: Session, exercise: schemas.ExerciseCreate):
    db_exercise = models.Exercise(**exercise.dict())
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

def get_exercises_by_muscle_group(db: Session, muscle_group: str):
    return db.query(models.Exercise).filter(models.Exercise.muscle_group == muscle_group).all()

def create_workout_plan(db: Session, workout_plan: schemas.WorkoutPlanCreate, user_id: int):
    db_workout_plan = models.WorkoutPlan(
        user_id=user_id,
        plan_name=workout_plan.plan_name
    )
    db.add(db_workout_plan)
    db.commit()
    db.refresh(db_workout_plan)
    
    # Add exercises to the workout plan
    for exercise_id in workout_plan.exercise_ids:
        db_workout_exercise = models.WorkoutPlanExercise(
            workout_plan_id=db_workout_plan.id,
            exercise_id=exercise_id
        )
        db.add(db_workout_exercise)
    
    db.commit()
    return db_workout_plan

def get_user_workout_plans(db: Session, user_id: int):
    return db.query(models.WorkoutPlan).filter(models.WorkoutPlan.user_id == user_id).all()

def create_nutrition_plan(db: Session, nutrition_plan: schemas.NutritionPlanCreate, user_id: int):
    db_nutrition_plan = models.NutritionPlan(
        user_id=user_id,
        plan_name=nutrition_plan.plan_name
    )
    db.add(db_nutrition_plan)
    db.commit()
    db.refresh(db_nutrition_plan)
    return db_nutrition_plan

def get_user_nutrition_plans(db: Session, user_id: int):
    return db.query(models.NutritionPlan).filter(models.NutritionPlan.user_id == user_id).all() 