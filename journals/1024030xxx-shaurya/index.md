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
