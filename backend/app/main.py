from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app import models
from app.database import Base, SessionLocal, engine
from app.routers import advice, auth, workouts

SEED_EXERCISES = [
    ("Barbell Back Squat", "legs"),
    ("Romanian Deadlift", "hamstrings"),
    ("Conventional Deadlift", "back"),
    ("Barbell Bench Press", "chest"),
    ("Incline Dumbbell Press", "chest"),
    ("Overhead Press", "shoulders"),
    ("Barbell Row", "back"),
    ("Pull-Up", "back"),
    ("Lat Pulldown", "back"),
    ("Barbell Curl", "biceps"),
    ("Triceps Pushdown", "triceps"),
    ("Leg Press", "legs"),
]


def seed_exercises() -> None:
    with SessionLocal() as db:
        if db.scalar(select(models.Exercise.id).limit(1)) is None:
            db.add_all(models.Exercise(name=n, muscle_group=g) for n, g in SEED_EXERCISES)
            db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Creates tables if missing. (Later we'll switch to Alembic migrations.)
    Base.metadata.create_all(bind=engine)
    seed_exercises()
    yield


app = FastAPI(title="IronCoach API", version="0.1.0", lifespan=lifespan)

# Open CORS for development so the Flutter web/emulator can call the API.
# Tighten this before any real deployment.
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(workouts.router)
app.include_router(advice.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
