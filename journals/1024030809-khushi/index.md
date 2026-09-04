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



