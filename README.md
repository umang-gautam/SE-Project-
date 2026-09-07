# AI-Powered Student Workload Balancer

UCS503P Software Engineering project, TIET Patiala, 2026-27 ODD.

Students enter subjects, topics, deadlines and available hours. A deterministic
engine turns that into a prioritised weekly study plan and re-balances it as
the student logs progress. A reasoning agent explains the plan in plain
language but is never allowed to change it.

Full proposal: [`project-proposal/main.pdf`](project-proposal/main.pdf).
Docs site: built from `docs/` and `journals/` by mkdocs on every push to `main`.

## Layout

| Path | What |
|---|---|
| `code/` | FastAPI backend. See [`docs/setup.md`](docs/setup.md) and [`docs/architecture.md`](docs/architecture.md). |
| `journals/<roll>-<name>/` | One folder per team member, `index.md` is the entry point. Published on the docs site. |
| `docs/` | Project documentation (mkdocs, Material theme). |
| `project-proposal/` | Proposal report, LaTeX. |
| `project-report-prototype-stage/`, `project-report-final/` | Later reports, not started. |

## Quick start (backend)

```sh
cd code
cp .env.example .env          # fill in Supabase URL and service key
docker compose up --build     # API on http://localhost:8000, Swagger at /docs
docker compose run --rm api python scripts/init_db.py   # tables in the local Postgres
```

Without Docker:

```sh
cd code
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

Tests, from the repo root: `pytest`.

## Docs site locally

```sh
pip install mkdocs-material mkdocs-literate-nav mkdocs-section-index \
  mkdocs-git-revision-date-localized-plugin mkdocs-git-authors-plugin mkdocstrings[python]
make docs        # or: mkdocs serve
```
