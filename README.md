# AI-Powered Student Workload Balancer

UCS503P Software Engineering project, TIET Patiala, 2026-27 ODD.

A student enters subjects, topics, deadlines and scores. A deterministic
scoring engine ranks every topic by how weak and how urgent it is, a planner
turns that into a weekly schedule of 30 to 60 minute sessions, and a LangGraph
agent rebalances the plan when sessions are missed, scores drop or deadlines
move. The agent explains its decisions and cannot bypass the business rules:
it only reaches the system through the service layer.

Blueprint: [`docs/project-blueprint.pdf`](docs/project-blueprint.pdf).
Docs site: built from `docs/` and `journals/` on every push to `main`.

## Layout

| Path | What |
|---|---|
| `code/backend/` | FastAPI API, scoring engine, planner, agent. [Architecture](docs/architecture.md) |
| `code/frontend/` | React app. [Frontend](docs/frontend.md) |
| `code/docker-compose.yml` | Both, one command |
| `journals/<roll>-<name>/` | One folder per team member, published on the docs site |
| `docs/` | mkdocs source |
| `project-proposal/` | Proposal report, LaTeX |

## Quick start

```sh
cd code/backend && cp .env.example .env     # add SUPABASE_URL and SUPABASE_KEY
cd .. && docker compose up --build          # http://localhost:8080
```

Without Docker, see [Setup](docs/setup.md). Tests run from the repo root with `pytest`.

## Team

Umang (frontend), Vriti (frontend), Khushi (backend API), Shaurya (scoring, agent, infrastructure).
