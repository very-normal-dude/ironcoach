from datetime import date as date_type

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------- Auth / users ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    weight_kg: float | None = None
    height_cm: float | None = None
    age: int | None = None
    goal: str | None = None


class UserProfileUpdate(BaseModel):
    weight_kg: float | None = Field(default=None, gt=0, lt=500)
    height_cm: float | None = Field(default=None, gt=0, lt=300)
    age: int | None = Field(default=None, ge=10, le=100)
    goal: str | None = Field(default=None, max_length=100)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Exercises ----------
class ExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    muscle_group: str


# ---------- Workouts ----------
class SetCreate(BaseModel):
    exercise_id: int
    weight_kg: float = Field(gt=0, le=1000)
    reps: int = Field(ge=1, le=30)


class WorkoutCreate(BaseModel):
    date: date_type | None = None  # defaults to today
    notes: str | None = Field(default=None, max_length=500)
    sets: list[SetCreate] = Field(min_length=1)


class SetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exercise_id: int
    weight_kg: float
    reps: int
    estimated_1rm_kg: float


class WorkoutOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date_type
    notes: str | None
    sets: list[SetOut]


class OneRMPoint(BaseModel):
    date: date_type
    best_estimated_1rm_kg: float


class OneRMResult(BaseModel):
    weight_kg: float
    reps: int
    formula: str
    estimated_1rm_kg: float
