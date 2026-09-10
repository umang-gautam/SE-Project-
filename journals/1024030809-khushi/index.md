\# Khushi's Journal



Roll No. 1024030809

Name: Khushi

## Phase 0 — Foundations: HTTP/API Fundamentals

**Status:** Complete

### What I did
- Learned core HTTP/API fundamentals as groundwork before touching any code — request/response cycle, REST principles, status codes, how clients and servers communicate
- Built the conceptual base needed to understand FastAPI's routing and request handling later

### Key decisions & reasoning
- Chose to learn fundamentals before scaffolding any project code, since I'm learning full-stack backend development from the ground up and wanted to understand *why* things work, not just copy commands

### Challenges & how I solved them
- N/A — this phase was primarily conceptual learning

### Next steps
- Move to environment setup and initial FastAPI scaffold

---

## Phase 1 — Environment Setup

**Status:** Complete

### What I did
- Set up the local development environment for the project
- Installed core packages: `fastapi`, `uvicorn`, `pydantic-settings`, `sqlalchemy`, `psycopg2-binary`
- Established the virtual environment

### Key decisions & reasoning
- **Decision:** Consolidated the virtual environment to live inside the repo itself.
  **Why:** Originally the code and venv were split across two different folders (OneDrive Desktop vs. local Desktop), causing path/dependency confusion. Moving everything under a single source of truth at `SE-Project-` fixed this.

### Challenges & how I solved them
- Faced confusion from having project files and the venv in different locations — resolved by consolidating everything into one repo folder on disk

### Next steps
- Scaffold the FastAPI project structure

---

## Phase 2 — FastAPI Project Scaffold

**Status:** Complete

### What I did
- Scaffolded the FastAPI backend with a strict layered architecture: `api/routes/`, `core/config.py`, `schemas/`, `services/`, `repositories/`, `models/`
- Set up the project to enforce one-directional layering: routes → services → repositories → database

### Key decisions & reasoning
- **Decision:** Enforced strict one-directional layering as a structural rule, not just a convention.
  **Why:** This matters especially for the LangGraph agent piece later — the agent will call services via tools and cannot access the database directly. Making this a structural constraint (rather than just a coding guideline) is a stronger design argument for the project defense.
- **Decision:** Used `pydantic-settings` for config management.
  **Why:** Learned it looks for `.env` relative to the working directory, not the file's location — important to remember when running commands from inside `code/` vs. the repo root.

### Challenges & how I solved them
- A `.env` file was briefly at risk of being committed with real credentials — learned that Notepad can silently save files as `.env.txt`, so filenames need to be quoted when creating `.env` to avoid this trap. Verified `.gitignore` properly excludes `.env`.

### Next steps
- Connect PostgreSQL and verify DB connectivity (Phase 3)

---

## 2026-09-04 — Phase 3 & 4: DB Connection Verified, Schema Design Complete

**Status:** Phase 3 Complete | Phase 4 Schema Designed (model code pending)

### What I did
- Verified PostgreSQL connection via SQLAlchemy; `test_db_connection.py` returned `Connection successful: (1,)`
- Designed the full 8-table schema for the workload balancer: `Student`, `Subject`, `Enrollment`, `Topic`, `Assignment`, `PerformanceRecord`, `StudyPlan`, `StudySession`
- Decided on SQLAlchemy 2.0 style (`Mapped[]` + `mapped_column`) for all models

### Key decisions & reasoning
- **Decision:** `StudyPlan` and `StudySession` are separate tables, not merged.
  **Why:** `StudyPlan` acts as an umbrella (the overall plan), while `StudySession` is the finer grain needed for adaptive rebalancing — sessions can be added/modified without restructuring the whole plan.
- **Decision:** `Subject` is a shared catalog; students connect to it via `Enrollment`.
  **Why:** Avoids duplicating subject data per student; supports a multi-student system cleanly.
- **Decision:** `Topic` hangs off `Subject`, not `Enrollment`.
  **Why:** Topics like "Linked Lists" are the same regardless of which student is enrolled — they shouldn't be duplicated per enrollment.
- **Decision:** `PerformanceRecord` links to `Topic`, not `Assignment`.
  **Why:** Mastery is tracked at the concept level, not the task level.
- **Decision:** `Assignment` is treated as a deadline/urgency tracker only, not a mastery signal.
  **Why:** In this academic context, assignments are formality tasks — they don't reliably reflect understanding, so they should drive urgency weighting in the scoring engine instead.

### Challenges & how I solved them
- Earlier had code and the virtual environment split across two different folders (OneDrive Desktop vs. local Desktop) — consolidated everything into the repo at `SE-Project-` with the venv living inside it.
- A `.env` file with DB credentials was briefly committed — rotated the password immediately and confirmed `.gitignore` now excludes `.env` properly.

### Next steps
- Write SQLAlchemy model code for all 8 tables in `code/app/models/` (one file per table + `__init__.py`)
- Re-verify DB connection before starting model code
- Move on to repository layer

---



## 2026-09-08 — Phase 5: Backend re-based on the project blueprint

**Status:** Complete

### What I did
- Moved the backend from `code/app` to `code/backend/app` so the frontend can live beside it under `code/frontend`. Added the full project blueprint as `docs/project-blueprint.pdf`; it is now the reference for every layer.
- Replaced the SQLAlchemy models and the compose Postgres with `schema.sql`, the blueprint's Supabase DDL: UUID keys, CHECK constraints on score, duration and status, cascading FKs.
- Rewrote `main.py` as an application factory: CORS for the Vite dev origin, a global handler that turns Supabase `HTTPStatusError`s into `{"status", "message"}` responses, `/health`. Routers get mounted as each entity lands.
- `config.py` now reads `SUPABASE_URL`, `SUPABASE_KEY`, `CORS_ORIGINS`, `DEBUG`. `DATABASE_URL` is gone.
- Updated `pyproject.toml` test paths and the backend CI workflow for the new folder.

### Key decisions & reasoning
- **Decision:** Schema lives in SQL, not ORM models.
  **Why:** The request path is Supabase REST. Models nobody queries through are documentation pretending to be code. `schema.sql` is what actually gets pasted into the Supabase SQL editor.
- **Decision:** Assignments hang off `topics`, not `subjects`.
  **Why:** Urgency is computed per topic. An assignment on a subject cannot tell the scoring engine which topic to prioritise.
- **Decision:** `/health` is a plain liveness probe again.
  **Why:** With no direct database, the per-dependency status from Phase 6 had one field left. Docker's healthcheck only reads the status code.

### Next steps
- Pydantic schemas with Create, Update and Response variants for all eight entities.

---

## 2026-09-08 — Phase 6: Pydantic schemas for all eight entities

**Status:** Complete

### What I did
- One schema module per entity under `app/schemas/`, each with a `Create` model (request body), an `Update` model (all fields optional, for PATCH) and a `Response` model (what a Supabase row looks like). Enrollments and performance records have no `Update`: you delete and re-create them.
- `app/schemas/__init__.py` re-exports everything so routes import from one place.
- 19 tests in `tests/test_schemas.py`: required fields, empty strings rejected, score bounded 0 to 100 inclusive, duration must be positive, session status restricted to pending/done/missed, and `model_validate` from a plain dict.
- `tests/conftest.py` provides a `TestClient` fixture for the route tests coming next.

### Key decisions & reasoning
- **Decision:** IDs are `str`, not `int` or `UUID`.
  **Why:** Supabase returns UUIDs as JSON strings. Parsing them into `uuid.UUID` and back buys nothing and makes every test fixture noisier.
- **Decision:** Validation rules mirror the CHECK constraints in `schema.sql`.
  **Why:** A bad request should fail with a 422 before it reaches the network, but the database stays the last line of defence.

### Next steps
- Repository layer: one module per table, plain httpx calls to PostgREST.

---

## 2026-09-09 — Phase 7: Repositories for students, subjects, enrollments, topics

**Status:** Complete

### What I did
- `app/repositories/student_repo.py`, `subject_repo.py`, `enrollment_repo.py`, `topic_repo.py`. Each exposes `create`, `get_all`, `get_by_id`, `update` (where the entity has an Update schema) and `delete`, plus the one lookup the domain needs: enrollments by student, topics by subject.
- Every function opens a short-lived `httpx.AsyncClient` from `core/supabase_client.py`, makes one PostgREST call, raises on non-2xx, and returns raw dicts. No validation, no defaults, no joins.

### Key decisions & reasoning
- **Decision:** A new client per call instead of a module-level singleton.
  **Why:** `httpx.AsyncClient` is cheap to build, and a singleton bound to one event loop breaks under `TestClient` and under uvicorn reloads. Learned this the hard way in the first scaffold.
- **Decision:** `get_by_id` returns `None`, `delete` returns a bool.
  **Why:** Routes decide what a missing row means (404). Repositories should not raise HTTP exceptions; they do not know they are inside an HTTP server.
- **Decision:** Filters are PostgREST query params like `id=eq.<uuid>`, never string-built URLs.
  **Why:** httpx encodes params; hand-built URLs are where injection and encoding bugs live.

### Next steps
- The other four repositories: assignments, performance records, study plans, study sessions.

---

## 2026-09-09 — Phase 8: Repositories for assignments, performance, plans, sessions

**Status:** Complete

### What I did
- `assignment_repo.py` (with `get_by_topic`), `performance_repo.py` (with `get_by_student` and `get_by_student_and_topic`), `study_plan_repo.py` (with `get_by_student`, newest first), `study_session_repo.py` (with `get_by_plan` and `create_many`).
- `create_many` posts a JSON array to PostgREST in one request; plan generation will insert dozens of sessions at once and a request per row would be silly.

### Key decisions & reasoning
- **Decision:** Plans are ordered by `start_date` descending at the repository.
  **Why:** "Most recent plan" is the only ordering anyone asks for. Doing it in the query keeps the agent's `get_plan` tool trivial.
- **Decision:** `get_by_student_and_topic` on performance records rather than fetching all and filtering.
  **Why:** Scoring calls it once per topic. Two `eq.` filters cost nothing server-side.

### Next steps
- Services and routes so the repositories are reachable over HTTP.

---

## 2026-09-10 — Phase 9: Service layer for all eight entities

**Status:** Complete

### What I did
- One service module per entity under `app/services/`. Each function takes plain dicts and ids, calls exactly one repository function, and returns what it returns.
- They are thin on purpose. The point of the layer is that routes and the agent both go through it, so business rules added later (duplicate-enrollment checks, plan archival) land in one place and apply to both callers.

### Key decisions & reasoning
- **Decision:** Services take `dict` payloads, not pydantic models.
  **Why:** Routes call `model_dump(exclude_unset=True)` so PATCH only sends the fields the client set. The agent builds dicts directly. One signature serves both.
- **Decision:** No service imports another service yet.
  **Why:** The cross-entity logic belongs to the scoring and planning services, which Shaurya is building on top of these.

### Next steps
- Routes for every entity, mounted on the app, with the students router tested end to end.

---

