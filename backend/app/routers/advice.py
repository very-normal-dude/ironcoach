from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import models
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/advice", tags=["advice"])


def build_user_summary(user: models.User, db: Session, days: int = 14) -> dict:
    """Compress the user's recent data into a small dict. This is what the LLM will see
    (we never send raw database rows)."""
    since = date.today() - timedelta(days=days)
    sessions = db.scalars(
        select(models.WorkoutSession)
        .where(models.WorkoutSession.user_id == user.id, models.WorkoutSession.date >= since)
        .options(selectinload(models.WorkoutSession.sets).selectinload(models.WorkoutSet.exercise))
    ).all()

    best_by_exercise: dict[str, float] = {}
    total_sets = 0
    for session in sessions:
        for s in session.sets:
            total_sets += 1
            name = s.exercise.name
            best_by_exercise[name] = max(best_by_exercise.get(name, 0), s.estimated_1rm_kg)

    return {
        "goal": user.goal,
        "weight_kg": user.weight_kg,
        "age": user.age,
        "period_days": days,
        "workouts_completed": len(sessions),
        "total_sets": total_sets,
        "best_estimated_1rm_kg": best_by_exercise,
    }


@router.post("")
def get_advice(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    summary = build_user_summary(user, db)

    # TODO (Week 4): replace this fake text with a real LLM call.
    #   1. put the system prompt in app/prompts/advice_system.txt
    #   2. send `summary` + the prompt to the LLM using settings.llm_api_key
    #   3. return the model's reply as "advice"
    fake_advice = (
        "MOCK ADVICE: You trained "
        f"{summary['workouts_completed']} time(s) in the last {summary['period_days']} days. "
        "Keep progressive overload in mind: add a little weight or a rep when sets feel easy."
    )
    return {"summary": summary, "advice": fake_advice, "is_mock": True}
