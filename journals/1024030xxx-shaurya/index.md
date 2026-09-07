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

---

## 2026-09-06 — Phase 10: Tests and CI

**Status:** Complete

### What I did
- Added `code/tests/` with six tests across four files, runnable with a bare `pytest` from the repo root and no credentials:
  - `test_health.py`: unconfigured DB and unreachable Supabase are reported in the body; an unreachable Postgres URL yields `error: ...` instead of an exception.
  - `test_students.py`: list, 404 on missing id, and POST validation (a bad email is rejected with 422 before the repository is ever called).
  - `test_models.py`: all eight tables build from the models.
  - `conftest.py`: sets dummy Supabase env vars so `Settings()` constructs, and provides a `TestClient`.
- Added `code/requirements-dev.txt` (just pytest) and `testpaths` in `pyproject.toml` so pytest does not try to collect `test_db_connection.py`, which is a manual script.
- Added `.github/workflows/backend.yml`: on push to main and on PRs touching `code/`, install, run pytest, build the Docker image, start it, and curl `/health`.

### Key decisions & reasoning
- **Decision:** Tests replace the repository layer with `monkeypatch`, not the HTTP client.
  **Why:** The repository is the boundary Khushi drew in Phase 2. Testing above it exercises routes, schemas and services together, which is where the logic lives. Mocking httpx would test Supabase's URL conventions instead.
- **Decision:** No pytest plugins, no fixtures beyond `client`.
  **Why:** Six tests do not need infrastructure. Add it when a test needs it.
- **Decision:** CI smoke-tests the built image, not just the build.
  **Why:** A Dockerfile that builds but produces an image that crashes on start is the most common container bug. Fifteen seconds of curl in CI catches it.
- **Decision:** Workflow triggers are path-filtered.
  **Why:** A journal edit should not spend CI minutes building a Docker image.

### Challenges & how I solved them
- My first health test monkeypatched a probe function to raise and asserted the endpoint still returned 200. It failed, correctly: the probes catch their own errors, the handler does not, and there is no reason it should. The test was asserting behaviour nobody designed. Rewrote it to use a real failure, an unreachable `DATABASE_URL`, which is what the code actually guards against.
- `get_engine()` is `lru_cache`d, so a test that changes `DATABASE_URL` must clear the cache before and after. Done in the test with a `try/finally`.

### Next steps
- Documentation: README, project index and setup pages describing what actually exists, and the mkdocs fixes so the journals appear on the site.

---

## 2026-09-07 — Phase 11: Documentation and site fixes

**Status:** Complete

### What I did
- Rewrote `README.md` to describe this project instead of the course template: what it is, repo layout, backend quick start with and without Docker, how to run tests and the docs site.
- Rewrote `docs/index.md` from the template's "Sum Function in C++" sample into a project overview with team, problem, the five components from the proposal, and a status table.
- Added `docs/architecture.md` (layers, the eight entities, health contract, containers and CI) and `docs/setup.md` (configure, run, test, add an entity).
- Restored `docs/journals` and `docs/assets` as symlinks. They had been committed as 9-byte text files containing the literal string `../journals`, almost certainly from a Windows checkout, so the published site had no journals and no logo.
- Pointed `mkdocs.yml` at this repository: site name, URL, repo link, copyright.
- Changed the bot identity in `.github/workflows/mkdocs.yml` from the template author's personal address to the generic `github-actions[bot]` address. Every `gh-pages` deploy had been showing up as authored by him.
- Removed the conda dependency from the `Makefile`. It hardcoded `~/miniconda3` and an env named `emacs`, so `make docs` failed on every machine but the template author's. It now just calls `mkdocs`.
- Built the site locally and confirmed all three journals render.

### Key decisions & reasoning
- **Decision:** Two short docs pages, not one long one.
  **Why:** Architecture is read once. Setup is read every time someone joins or reinstalls. Different audiences, different pages.
- **Decision:** Keep the template's project-selection criteria page.
  **Why:** It is the rubric the proposal was written against, and it explains why the project is scoped the way it is.
- **Decision:** Leave `pyproject.toml`'s package name and author alone.
  **Why:** Nothing consumes them, and the pytest configuration in that file is the only part that matters. Changing metadata nobody reads is churn.

### Challenges & how I solved them
- mkdocs flagged `[Journals](journals/)` as an unrecognised link because the folder has no `index.md`. Linked each member's journal directly instead.

### Next steps
- Workload scoring engine in `app/services/`, driven by the models and the compose Postgres.
- Frontend integration against the API once its pages are restored.
