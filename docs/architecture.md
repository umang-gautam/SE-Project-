# Architecture

Two deployable units under `code/`: a FastAPI backend and a React frontend.
The design follows the [project blueprint](project-blueprint.pdf).

```
React (Vite / nginx)  ── /api ──►  FastAPI routes
                                       │
                                   services  ◄── LangGraph agent (tools only)
                                       │
                                  repositories
                                       │ httpx
                                  Supabase (PostgREST)
```

**One rule:** routes → services → repositories → database. No layer skips ahead.
The agent calls services through `app/agent/tools.py` and has no import path
to repositories or the Supabase client. A test scans the agent package's
source to enforce this.

## Backend layers (`code/backend/app`)

| Layer | Folder | Does | Does not |
|---|---|---|---|
| Routes | `api/routes/` | Validate with a schema, call one service, map `None`/`False` to 404 | Touch httpx or Supabase |
| Schemas | `schemas/` | `XCreate`, `XUpdate` (all optional), `XResponse` per entity; scoring and agent payloads | Hold logic |
| Services | `services/` | CRUD pass-through per entity; `scoring_service` (pure), `plan_service` (allocation + orchestration), `agent_service` (runs the graph) | Know about HTTP |
| Repositories | `repositories/` | One module per table, httpx calls to PostgREST, raw dicts back | Validate or raise HTTP errors |
| Agent | `agent/` | `tools.py` wraps services; `graph.py` is the LangGraph state machine | Import repositories |
| Core | `core/` | `config.py` (pydantic-settings from `.env`), `supabase_client.py` | Anything else |

## Data model (`code/backend/schema.sql`)

Eight tables, UUID keys, cascading deletes.

| Table | Purpose | Notable columns |
|---|---|---|
| `students` | Identity | unique `email` |
| `subjects` | Shared catalog | unique `code` |
| `enrollments` | student ↔ subject | unique pair |
| `topics` | Sub-units of a subject | `subject_id` |
| `assignments` | Deadline signal per topic | `topic_id`, `due_date` |
| `performance_records` | Score per student per topic over time | `score` 0–100 |
| `study_plans` | One planning window per student | `start_date`, `end_date` |
| `study_sessions` | Blocks inside a plan | `date`, `duration_minutes` > 0, `status` in pending/done/missed |

Why `assignments` hang off `topics`: urgency is computed per topic.
Why `study_plans` and `study_sessions` are separate: the agent rebalances at
session grain without recreating the plan.

## Scoring and planning

- **Mastery** = mean of a topic's scores / 100.
- **Urgency** = 1 at or past the nearest due date, 0 at 30 days out, linear between.
- **Priority** = 100 × (0.6 × (1 − mastery) + 0.4 × urgency).
- **Allocation** splits `hours_per_day × num_days` across topics in proportion to
  priority, in 30–60 minute sessions, placed on the least-loaded day.

All of this is pure Python in `scoring_service.py` and `plan_service.allocate_sessions`,
tested without any network.

## Agent

`POST /agent/rebalance` runs a LangGraph graph:

```
detect_change ──[changes_needed]──► re_score ► re_plan ► explain_decision ► END
              └──[no]──► no_change ► END
```

Triggers: `missed_session` (always), `low_score` (< 50), `new_assignment`
(≤ 7 days), `manual` (always). Every node is deterministic; the explanation
is plain text listing the reason and the top three topics.

## API surface

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness |
| CRUD | `/students`, `/subjects`, `/topics`, `/assignments`, `/enrollments`, `/study-plans`, `/study-sessions` | Resource management, plus `by-<parent>/{id}` lookups |
| POST | `/performance/` | Log a score |
| GET | `/students/{id}/scores` | Scored topics, highest priority first |
| POST | `/study-plans/generate` | Score, allocate, persist a plan |
| PATCH | `/study-sessions/{id}` | Mark done/missed |
| POST | `/agent/rebalance` | Run the agent |

Interactive docs at `/docs` when the backend is running.

## Frontend (`code/frontend/src`)

`api/client.js` is the only module that calls `fetch`. Pages under `pages/`
(Dashboard, Subjects, PerformanceEntry, StudyPlanView), shared pieces under
`components/` (TopicCard, ScoreBadge, SessionBlock), and `hooks/useStudyPlan.js`
for plan and session state. In development Vite proxies `/api` to port 8000;
in the container nginx does the same, so the client never changes.

## Containers and CI

- `code/backend/Dockerfile`: python 3.12-slim, non-root, healthcheck on `/health`.
- `code/frontend/Dockerfile`: Node build stage, nginx serve stage with the `/api` proxy.
- `code/docker-compose.yml`: both, frontend on 8080, backend internal only.
- `.github/workflows/backend.yml`: pytest, image build, smoke test. `frontend.yml`: npm build, image build.
- `.github/workflows/mkdocs.yml`: publishes this site on push to `main`.
