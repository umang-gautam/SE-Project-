# Shaurya's Journal

Roll No. 1024030xxx

Name: Shaurya

Backend track. Picks up from Khushi's Phase 4 (schema designed, models pending).

---

## 2026-09-01 — Phase 5: Dependency and encoding cleanup

**Status:** Complete

### What I did
- Re-saved `code/requirements.txt` as UTF-8 with LF line endings. It had been written as UTF-16 with CRLF from Windows, which pip cannot parse on Linux or in a Docker build.
- Added the two packages the code already imports but never declared: `httpx` (used by every repository to call Supabase) and `email-validator` (required by pydantic's `EmailStr`).
- Stripped the UTF-8 byte-order mark from 29 Python files under `code/app/`. Harmless to Python, noisy in diffs and breaks some linters.
- Added `code/.env.example` documenting the three environment variables the app reads.

### Key decisions & reasoning
- **Decision:** Pin `httpx` and `email-validator` to exact versions like the rest of the file.
  **Why:** The file is a lockfile in spirit. Mixing pinned and floating versions makes Docker builds non-reproducible.
- **Decision:** Ship `.env.example` instead of documenting variables only in prose.
  **Why:** A new teammate copies one file and fills in blanks. Also makes it obvious that `.env` itself must stay untracked.

### Challenges & how I solved them
- `pip install -r requirements.txt` failed with an encoding error before anything else could be tested. Confirmed with `file requirements.txt` that it was UTF-16, converted with Python.

### Next steps
- Make the API start without `DATABASE_URL`, since Supabase REST is the real data path.
- Turn `/health` into something a container orchestrator can actually use.

---

## 2026-09-02 — Phase 6: Lazy DB engine and a real health check

**Status:** Complete

### What I did
- `app/core/database.py` no longer creates the SQLAlchemy engine at import time. `get_engine()` builds it on first call and raises a clear error if `DATABASE_URL` is unset.
- Replaced `declarative_base()` with a `DeclarativeBase` subclass, the SQLAlchemy 2.0 form, so the models in the next phase can use `Mapped[]` annotations against it.
- `/health` now reports three fields: `status`, `database`, `supabase`. Each backing service is probed and reported as `ok`, `unconfigured`, or `error: <reason>`.
- Removed the duplicate `test_db_connection.py` at the repo root; the one inside `code/` is the one the journal and `pyproject.toml` refer to.

### Key decisions & reasoning
- **Decision:** `/health` always returns HTTP 200 and puts the dependency state in the body.
  **Why:** A Docker or Kubernetes healthcheck that fails when Supabase blips would restart a perfectly good container. Liveness and dependency status are different questions.
- **Decision:** Keep `DATABASE_URL` optional.
  **Why:** The request path uses Supabase REST. Direct Postgres access is only for schema work and local checks, and the API must boot without it.

### Challenges & how I solved them
- `from app.core.database import Base` would have crashed on `create_engine(None)` before any model code could load. Making the engine lazy fixed this without touching callers.

### Next steps
- Write the eight SQLAlchemy models against the new `Base`.

---

## 2026-09-03 — Phase 7: SQLAlchemy models for the eight tables

**Status:** Complete

### What I did
- Wrote one model file per table under `code/app/models/`: `Student`, `Subject`, `Enrollment`, `Topic`, `Assignment`, `PerformanceRecord`, `StudyPlan`, `StudySession`. All use the SQLAlchemy 2.0 `Mapped[]` + `mapped_column()` style against the `Base` from Phase 6.
- Column names and types mirror the pydantic schemas in `app/schemas/`, so the model is a faithful description of what Supabase already holds.
- `app/models/__init__.py` imports every model, so a single import registers the full schema on `Base.metadata`.
- Verified with `Base.metadata.create_all()` against an in-memory SQLite engine that all eight tables build with no circular-import or FK errors.

### Key decisions & reasoning
- **Decision:** Keep Phase 4's schema exactly. `Topic` under `Subject`, `PerformanceRecord` on `Topic`, `Assignment` as urgency only, `StudyPlan` and `StudySession` separate.
  **Why:** Those decisions were argued out already; the models should encode them, not reopen them. Each file carries a one-line docstring restating the reason so it survives without the journal.
- **Decision:** `ON DELETE CASCADE` on every child FK, `SET NULL` on the self-reference in `StudySession`.
  **Why:** Deleting a student should take their plans and sessions with them. Deleting a session that others were rebalanced from should not delete those newer sessions.
- **Decision:** Unique constraint on `(student_id, subject_id)` in `Enrollment`.
  **Why:** Enrolling twice in the same subject is always a bug, and a DB constraint is cheaper than app-side checks.
- **Decision:** Models are not wired into the repositories.
  **Why:** The API stays on Supabase REST. The models exist for schema-as-code, local Postgres, and the future scoring engine. Rewriting eight repositories is a separate, deliberate change.

### Challenges & how I solved them
- `Mapped[str | None]` needs Python 3.10+. Confirmed the Dockerfile in the next phase will pin 3.12 so this never bites in a container.

### Next steps
- Containerise the API so the same image runs locally, in CI, and on a host.

---

## 2026-09-04 — Phase 8: Containerising the API

**Status:** Complete

### What I did
- Added `code/Dockerfile`: `python:3.12-slim`, requirements installed in their own layer, app copied after, runs as a non-root `api` user, exposes 8000, runs uvicorn.
- Added `code/.dockerignore` so the venv, `.env`, tests and the PowerShell scaffold never end up in the image.
- Added `code/scripts/init_db.py`, which runs `Base.metadata.create_all()` against `DATABASE_URL`. This is how a fresh Postgres gets the schema in the next phase.
- Built the image and confirmed: it boots without `DATABASE_URL`, runs as `api` not root, and `GET /health` returns `{"status":"ok","database":"unconfigured","supabase":"error: ConnectError"}` when pointed at a dead Supabase URL. That last part is the point: the container stays up and tells you what is wrong.

### Key decisions & reasoning
- **Decision:** Copy `requirements.txt` and install before copying `app/`.
  **Why:** Docker caches layers top-down. Code changes daily, dependencies weekly. This ordering makes a rebuild after a code edit take seconds.
- **Decision:** Non-root user inside the container.
  **Why:** Costs two lines and removes a whole class of container-escape concerns. Hosts and CI scanners increasingly refuse root images.
- **Decision:** `HEALTHCHECK` hits `/health` and only checks for a 200.
  **Why:** Same reasoning as Phase 6. Docker's healthcheck decides whether to restart the container; a dead Supabase should not trigger that.
- **Decision:** `.env.example` is excluded from the image, `.env` too.
  **Why:** Config comes in through environment variables at run time. Baking any env file into an image is how secrets leak into registries.

### Challenges & how I solved them
- First build attempt copied `scripts/` before the folder existed. Created `init_db.py` first, then built.

### Next steps
- `docker-compose.yml` with the API and a Postgres, so the whole backend runs with one command.

---

## 2026-09-05 — Phase 9: docker-compose with Postgres

**Status:** Complete

### What I did
- Added `code/docker-compose.yml` with two services: `api` (built from the Dockerfile) and `db` (`postgres:16-alpine` with a named volume and a `pg_isready` healthcheck). The API waits for the DB to be healthy before starting.
- `api` reads Supabase values from `.env` and gets `DATABASE_URL` injected by compose, pointing at the `db` service.
- Ran the full loop: `docker compose up --build`, then `docker compose run --rm api python scripts/init_db.py`. Postgres ended up with all eight tables and `/health` reported `"database": "ok"`.
- Updated `.env.example` with the `DATABASE_URL` to use when running uvicorn outside compose against the compose Postgres.

### Key decisions & reasoning
- **Decision:** Postgres in compose is for schema work and local experiments. The API's request path still goes to Supabase.
  **Why:** Agreed scope. The repositories are not rewritten. Having a real Postgres locally lets the scoring engine and any future SQLAlchemy code be developed and tested without touching the shared Supabase project.
- **Decision:** Hardcode `balancer/balancer` credentials in compose.
  **Why:** They only ever bind to localhost on a dev machine. Parameterising them would add indirection for nobody.
- **Decision:** `depends_on` with `condition: service_healthy` rather than a retry loop in the app.
  **Why:** Compose already solves startup ordering. App-side retry logic is code that has to be maintained.

### Challenges & how I solved them
- `python scripts/init_db.py` inside the container failed with `No module named 'app'`. Python puts the script's own folder on `sys.path`, not the working directory. Fixed by setting `ENV PYTHONPATH=/app` in the Dockerfile, which also makes any future script under `scripts/` work the same way.

### Next steps
- Tests that run without Supabase credentials, and a GitHub Actions workflow that runs them and builds the image on every push.
