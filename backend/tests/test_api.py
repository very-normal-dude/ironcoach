import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import main
from app.database import Base, get_db


@pytest.fixture()
def client():
    # Fresh in-memory database for every test, so tests never touch real data.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False)
    Base.metadata.create_all(bind=engine)

    # point seeding + requests at the test DB
    main.SessionLocal = TestingSession
    main.seed_exercises()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[get_db] = override_get_db
    yield TestClient(main.app)
    main.app.dependency_overrides.clear()


def register_and_login(client, email="a@test.com", password="password123"):
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201, r.text
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_duplicate_email_rejected(client):
    register_and_login(client)
    r = client.post("/auth/register", json={"email": "a@test.com", "password": "password123"})
    assert r.status_code == 409


def test_wrong_password(client):
    register_and_login(client)
    r = client.post("/auth/login", data={"username": "a@test.com", "password": "wrongwrong"})
    assert r.status_code == 401


def test_protected_route_needs_token(client):
    assert client.get("/workouts").status_code == 401


def test_full_workout_flow(client):
    headers = register_and_login(client)
    exercises = client.get("/exercises").json()
    assert len(exercises) > 0
    bench = next(e for e in exercises if "Bench" in e["name"])

    r = client.post(
        "/workouts",
        headers=headers,
        json={"sets": [{"exercise_id": bench["id"], "weight_kg": 80, "reps": 8}]},
    )
    assert r.status_code == 201, r.text
    assert r.json()["sets"][0]["estimated_1rm_kg"] == 101.3  # 80 * (1 + 8/30)

    assert len(client.get("/workouts", headers=headers).json()) == 1

    progress = client.get(f"/exercises/{bench['id']}/progress", headers=headers).json()
    assert len(progress) == 1 and progress[0]["best_estimated_1rm_kg"] == 101.3


def test_unknown_exercise_rejected(client):
    headers = register_and_login(client)
    r = client.post(
        "/workouts",
        headers=headers,
        json={"sets": [{"exercise_id": 9999, "weight_kg": 50, "reps": 5}]},
    )
    assert r.status_code == 404


def test_users_cannot_see_each_others_workouts(client):
    h1 = register_and_login(client, "one@test.com")
    h2 = register_and_login(client, "two@test.com")
    ex = client.get("/exercises").json()[0]
    client.post(
        "/workouts", headers=h1,
        json={"sets": [{"exercise_id": ex["id"], "weight_kg": 60, "reps": 5}]},
    )
    assert client.get("/workouts", headers=h2).json() == []


def test_advice_is_mock_for_now(client):
    headers = register_and_login(client)
    r = client.post("/advice", headers=headers)
    assert r.status_code == 200 and r.json()["is_mock"] is True


def test_1rm_calculator_endpoint(client):
    r = client.get("/tools/1rm", params={"weight_kg": 100, "reps": 10})
    assert r.json()["estimated_1rm_kg"] == 133.3
