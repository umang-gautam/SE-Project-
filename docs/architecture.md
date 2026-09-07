# Backend architecture

FastAPI application in `code/app/`. One rule holds everything together:
**layers only call downward.**

```
api/routes  →  services  →  repositories  →  Supabase (PostgREST over httpx)
   ↑
schemas (pydantic request/response models)
```

| Layer | Folder | Responsibility |
|---|---|---|
| Routes | `app/api/routes/` | HTTP only. Parse the request, call one service function, map `None` to 404. |
| Schemas | `app/schemas/` | Pydantic models. `XCreate` is the request body, `XOut` is the response. |
| Services | `app/services/` | Business logic. Today they are thin; the workload engine will live here. |
| Repositories | `app/repositories/` | Data access. Async httpx calls to Supabase's REST API. Nothing above this layer knows about Supabase. |
| Models | `app/models/` | SQLAlchemy 2.0 models. Schema-as-code for the same eight tables; used by `scripts/init_db.py` and by any future SQL-side logic. |
| Core | `app/core/` | `config.py` (settings from `.env`), `database.py` (lazy engine, `Base`), `supabase_client.py`. |

The one-directional rule matters most for the reasoning agent: it will call
services through tools and will never touch a repository or the database.

## Entities

Eight tables, mirrored by the routes, schemas and models:

| Table | Purpose | Notes |
|---|---|---|
| `students` | Who | Unique email |
| `subjects` | Shared catalog | Credits and weekly effort feed the scoring |
| `enrollments` | Student ↔ subject | Unique per pair, optional target grade |
| `topics` | Belong to a subject | Difficulty 1-3, estimated hours |
| `assignments` | Deadlines per subject | Urgency signal only, not mastery |
| `performance_records` | Score per student per topic | Mastery signal, by concept |
| `study_plans` | One per student-week | Umbrella for sessions |
| `study_sessions` | Scheduled blocks within a plan | `rebalanced_from_session_id` links replacements |

The reasoning behind each choice is in Khushi's journal, Phase 4.

## Health

`GET /health` always returns 200 with per-dependency status:

```json
{"status": "ok", "database": "unconfigured", "supabase": "error: ConnectError"}
```

Docker's `HEALTHCHECK` and CI read only the status code. Humans read the body.

## Containers and CI

- `code/Dockerfile`: `python:3.12-slim`, non-root, uvicorn on 8000.
- `code/docker-compose.yml`: the API plus a local Postgres for schema work. The request path still uses Supabase.
- `.github/workflows/backend.yml`: pytest, image build, and a start-and-curl smoke test on every push or PR touching `code/`.
- `.github/workflows/mkdocs.yml`: builds this site to the `gh-pages` branch on every push to `main`.
