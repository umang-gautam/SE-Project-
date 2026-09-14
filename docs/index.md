![Tiet Logo](assets/tiet-logo.svg){ .tiet-logo }

**UCS503: Software Engineering (Project)**
**TIET Patiala**

# AI-Powered Student Workload Balancer

**Team**: Umang (1024030805), Vriti (1024030801), Khushi (1024030809), Shaurya (1024030xxx)

## The problem

Students juggling several subjects plan their week by hand, and the plan goes
stale the moment they fall behind. Most tools do not adapt to actual progress,
spread effort unevenly across subjects, and never explain *why* a plan looks the
way it does.

## What we built

1. **Scoring engine.** Every topic gets a priority from how weak the student is in it and how close its deadlines are.
2. **Planner.** A time budget becomes a schedule of 30 to 60 minute sessions, heaviest topics first, spread evenly across days.
3. **Rebalancing agent.** A LangGraph state machine watches for missed sessions, low scores and new deadlines, regenerates the plan when warranted, and explains what changed.
4. **Web app.** Dashboard of ranked topics, subject and topic management, score entry, and a study plan view with status tracking and a rebalance button.

The agent's only path into the system is the service layer. It cannot touch the
database. This is enforced by a test, not a convention.

## Where things are

- [Architecture](architecture.md): layers, data model, scoring, agent, API.
- [Setup](setup.md): running it, with or without Docker.
- [Frontend](frontend.md): pages, components, how `/api` reaches the backend.
- [Project blueprint](project-blueprint.pdf): the design this follows.
- Journals: [Umang](journals/1024030805-umang/index.md), [Vriti](journals/1024030801-vriti/index.md), [Khushi](journals/1024030809-khushi/index.md), [Shaurya](journals/1024030xxx-shaurya/index.md).
- [Project selection criteria](criteria-for-project-selection.md): the course rubric.

## Status (14 September 2026)

| Area | State |
|---|---|
| Backend API | CRUD for all eight entities, scores, plan generation, agent endpoint. 71 tests. |
| Scoring and planning | Done, pure functions, unit tested |
| Agent | Deterministic LangGraph graph, four triggers, import boundary enforced by test |
| Frontend | Four pages wired to the API, shared components, plan hook |
| Containers and CI | Backend and frontend images, compose, two path-filtered workflows |
| Deployment | Not started. Blueprint targets Render or Railway for the backend, Vercel for the frontend. |
| Prototype and final reports | Not started |
