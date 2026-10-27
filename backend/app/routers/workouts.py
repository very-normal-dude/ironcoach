from collections import defaultdict
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.services.one_rm import estimate_1rm

router = APIRouter(tags=["workouts"])


@router.get("/exercises", response_model=list[schemas.ExerciseOut])
def list_exercises(db: Session = Depends(get_db)):
    return db.scalars(select(models.Exercise).order_by(models.Exercise.name)).all()


@router.get("/tools/1rm", response_model=schemas.OneRMResult)
def calculate_1rm(
    weight_kg: float = Query(gt=0, le=1000),
    reps: int = Query(ge=1, le=30),
    formula: str = Query(default="epley", pattern="^(epley|brzycki)$"),
):
    """Quick calculator, no login needed."""
    value = estimate_1rm(weight_kg, reps, formula)
    return schemas.OneRMResult(
        weight_kg=weight_kg, reps=reps, formula=formula, estimated_1rm_kg=value
    )


@router.post("/workouts", response_model=schemas.WorkoutOut, status_code=201)
def create_workout(
    data: schemas.WorkoutCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise_ids = {s.exercise_id for s in data.sets}
    found = set(
        db.scalars(select(models.Exercise.id).where(models.Exercise.id.in_(exercise_ids))).all()
    )
    missing = exercise_ids - found
    if missing:
        raise HTTPException(status_code=404, detail=f"Unknown exercise id(s): {sorted(missing)}")

    session = models.WorkoutSession(
        user_id=user.id, date=data.date or date.today(), notes=data.notes
    )
    for s in data.sets:
        session.sets.append(
            models.WorkoutSet(
                exercise_id=s.exercise_id,
                weight_kg=s.weight_kg,
                reps=s.reps,
                estimated_1rm_kg=estimate_1rm(s.weight_kg, s.reps),
            )
        )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/workouts", response_model=list[schemas.WorkoutOut])
def list_workouts(
    limit: int = Query(default=30, ge=1, le=200),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = (
        select(models.WorkoutSession)
        .where(models.WorkoutSession.user_id == user.id)
        .options(selectinload(models.WorkoutSession.sets))
        .order_by(models.WorkoutSession.date.desc(), models.WorkoutSession.id.desc())
        .limit(limit)
    )
    return db.scalars(stmt).all()


@router.delete("/workouts/{workout_id}", status_code=204)
def delete_workout(
    workout_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.get(models.WorkoutSession, workout_id)
    if session is None or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Workout not found")
    db.delete(session)
    db.commit()


@router.get("/exercises/{exercise_id}/progress", response_model=list[schemas.OneRMPoint])
def exercise_progress(
    exercise_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Best estimated 1RM per day for one exercise. This feeds the progress chart."""
    rows = db.execute(
        select(models.WorkoutSession.date, models.WorkoutSet.estimated_1rm_kg)
        .join(models.WorkoutSet, models.WorkoutSet.session_id == models.WorkoutSession.id)
        .where(
            models.WorkoutSession.user_id == user.id,
            models.WorkoutSet.exercise_id == exercise_id,
        )
    ).all()
    best_per_day: dict[date, float] = defaultdict(float)
    for day, one_rm in rows:
        best_per_day[day] = max(best_per_day[day], one_rm)
    return [
        schemas.OneRMPoint(date=day, best_estimated_1rm_kg=value)
        for day, value in sorted(best_per_day.items())
    ]
