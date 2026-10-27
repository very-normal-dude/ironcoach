# IronCoach: Shared Context for AI Assistants (and humans)

> HOW TO USE: paste this whole file into your AI chat at the START of every session.
> At the END of a session, ask your AI: "Update the Decisions log and Status sections of
> this file with what we changed", then commit the updated file. This file is the shared
> memory of the project. Both AIs read the same file, so they stay in sync.

## 1. The project

IronCoach is a mobile app (Flutter) that lets users log strength workouts and meals.
A Python/FastAPI backend stores the data, calculates 1RM (one-rep max), and (later) sends a
compact summary of the user's data to an LLM to produce personalised training and nutrition
advice and a chat assistant. Future idea: rep counting with the camera.

## 2. Team split

- Backend (Python, FastAPI, SQLAlchemy): [MADEAN]
- Mobile app (Flutter, Dart): [NOUR]
- Supervisor: [RYAD]

## 3. Hard rules (AIs: follow these)

1. Budget is $0. Suggest only free tools, free tiers, and free/open datasets. Never suggest paid plans.
2. Never commit secrets (.env, API keys). Real keys live only in each developer's local `.env`.
3. The API contract is the source of truth: `docs/openapi.json` (generated from the backend code)
   plus the live docs at http://127.0.0.1:8000/docs. Do NOT invent endpoints or field names.
4. Do NOT rename or remove an API field on your own. If a change is needed, tell your human,
   who coordinates with the other developer. Then update this file and regenerate openapi.json.
5. Mobile and backend developers work in separate folders (`mobile/`, `backend/`) to avoid merge conflicts.
6. Before writing code that touches data, check Section 5 (Glossary) and use those exact names.

## 4. Naming conventions

| Thing                      | Convention                                      | Example                                             |
| -------------------------- | ----------------------------------------------- | --------------------------------------------------- |
| JSON fields and DB columns | snake_case                                      | `muscle_group`, `weight_kg`                         |
| Units                      | always in the field name                        | `weight_kg`, `height_cm`, `quantity_g`, `protein_g` |
| IDs                        | integers                                        | `"exercise_id": 4`                                  |
| Dates                      | ISO string `YYYY-MM-DD`                         | `"2026-10-26"`                                      |
| Date-times                 | ISO 8601, UTC                                   | `"2026-10-26T14:30:00Z"`                            |
| Endpoint paths             | plural nouns, lowercase                         | `/workouts`, `/exercises`                           |
| Errors                     | JSON `{"detail": "message"}`                    | 401, 404, 409, 422                                  |
| Dart classes               | PascalCase, same noun as backend                | `Workout`, `WorkoutSet`, `Exercise`                 |
| Dart fields                | camelCase, mapped from snake_case in `fromJson` | `estimated1rmKg` <- `estimated_1rm_kg`              |

## 5. Glossary: one name per concept

| Concept                        | DB table               | API name / field                            | Dart class       |
| ------------------------------ | ---------------------- | ------------------------------------------- | ---------------- |
| User                           | users                  | `/auth/me`, `user`                          | `User`           |
| Exercise                       | exercises              | `/exercises`, `exercise_id`, `muscle_group` | `Exercise`       |
| Workout (one gym session)      | workout_sessions       | `/workouts`, `workout`                      | `Workout`        |
| Set (one set inside a workout) | workout_sets           | `sets[]`, `weight_kg`, `reps`               | `WorkoutSet`     |
| Estimated one-rep max          | column on workout_sets | `estimated_1rm_kg`                          | `estimated1rmKg` |
| Food (values per 100 g)        | foods                  | `calories`, `protein_g`, `carbs_g`, `fat_g` | `Food`           |
| Meal log entry                 | meal_logs              | `food_id`, `quantity_g`                     | `MealLog`        |
| User goal                      | users.goal             | `goal` (e.g. `build_muscle`)                | `goal`           |

## 6. Auth

- `POST /auth/register`: JSON `{email, password}`
- `POST /auth/login`: **form-encoded** (not JSON): `username` (the email) and `password`. Returns `{access_token, token_type}`
- All protected routes need header: `Authorization: Bearer <access_token>`
- Android emulator reaches the backend at `http://10.0.2.2:8000` (not localhost).

## 7. Endpoints (v0.1). Full details in docs/openapi.json

| Method      | Path                                 | Auth |
| ----------- | ------------------------------------ | ---- |
| POST        | /auth/register                       | no   |
| POST        | /auth/login                          | no   |
| GET / PATCH | /auth/me                             | yes  |
| GET         | /exercises                           | no   |
| GET         | /tools/1rm?weight_kg=&reps=&formula= | no   |
| POST / GET  | /workouts                            | yes  |
| DELETE      | /workouts/{id}                       | yes  |
| GET         | /exercises/{id}/progress             | yes  |
| POST        | /advice (MOCK for now)               | yes  |

## 8. Status

- [x] Backend skeleton: auth, workouts, 1RM, progress, mock advice, 13 tests passing
- [ ] Exercise library import (free-exercise-db, public domain)
- [ ] Foods + meal logging (USDA FoodData Central, CC0)
- [ ] Real LLM call in /advice (free-tier provider)
- [ ] Chat endpoint
- [ ] Flutter screens: [fill in]

## 9. Decisions log (newest first; AIs: add a line when something is decided)

- 2026-10-26: Budget is $0. SQLite for development; PostgreSQL optional later.
- 2026-10-26: Exercise data source = free-exercise-db (Unlicense). Food data = USDA FoodData Central (CC0).
- 2026-10-26: openGym (AGPL v3) is used for ideas only. We do not copy its code or its images.
