![Tiet Logo](assets/tiet-logo.svg){ .tiet-logo }

**UCS503: Software Engineering (Project)**
**TIET Patiala**

# AI-Powered Student Workload Balancer

**Team**: Umang (1024030805), Khushi (1024030809), Shaurya (1024030xxx)

## The problem

Students juggling several subjects and deadlines plan their week by hand, and
the plan goes stale the moment they fall behind. Most tools do not adapt to
actual progress, distribute effort unevenly across subjects, and never explain
*why* a plan looks the way it does.

## What we are building

A web application with five parts:

1. **Student input portal** for subjects, topics, deadlines, assignments and available hours.
2. **Deterministic workload engine** that scores topics by deadline proximity, weight and past performance, and produces a prioritised weekly plan.
3. **Adaptive feedback loop** that re-balances the remaining plan when sessions are completed or missed.
4. **Reasoning agent** (LangGraph) that explains the plan. It can read the engine's output but cannot bypass it.
5. **Progress dashboard** for plan adherence and upcoming priorities.

The full argument is in the [project proposal](https://github.com/umang-gautam/SE-Project-/blob/main/project-proposal/main.pdf).

## Where things are

- [Architecture](architecture.md): the backend's layers and data model.
- [Setup](setup.md): running the backend locally, with or without Docker.
- Journals, weekly per member: [Umang](journals/1024030805-umang/index.md), [Khushi](journals/1024030809-khushi/index.md), [Shaurya](journals/1024030xxx-shaurya/index.md).
- [Project selection criteria](criteria-for-project-selection.md): the course rubric this project was chosen against.

## Status (September 2026)

| Area | State |
|---|---|
| Backend API | CRUD for all eight entities over Supabase, containerised, tested in CI |
| Data model | Eight tables designed and encoded as SQLAlchemy models |
| Frontend | React + Vite, eight module pages, in progress (see Umang's journal) |
| Workload engine | Not started |
| Reasoning agent | Not started |
