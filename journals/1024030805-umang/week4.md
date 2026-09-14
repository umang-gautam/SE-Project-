# Week 4: Frontend Rebuild on the Blueprint

## Work Done

- Re-created the frontend under `code/frontend` next to the backend, following the blueprint's folder layout: `src/pages`, `src/components`, `src/api`, `src/hooks`.
- Scaffolded with Vite 6, React 19, react-router 7 and Tailwind 3. Tailwind replaces the hand-written global CSS from week 1.
- Built the app shell: an always-visible indigo nav bar with links to Dashboard, Subjects, Scores and Study Plan, and a `<Routes>` block that swaps the page.
- Added placeholder pages for all four routes so the shell builds and navigation can be clicked through before any API work.
- Vite dev server proxies `/api` to the FastAPI backend on port 8000, so pages never hardcode a backend URL.
- Verified `npm run build` produces a clean production bundle.

## Next Steps

- Single API client module covering every backend endpoint.
- Dashboard page showing scored topics.

## API Client (Sept 9)

- Added `src/api/client.js`, the single module every page imports for backend calls. Nothing else in the frontend calls `fetch` directly.
- One `request()` helper sets JSON headers, treats 204 as `null`, and throws an `Error` carrying the backend's `detail` or `message` so pages can show it verbatim.
- Named exports per endpoint group: students (including `fetchStudentScores`), subjects, topics, assignments, enrollments, performance, study plans (including `generatePlan`), study sessions (`updateSession`), and `triggerRebalance` for the agent.
- Paths mirror the backend routers exactly, including the `by-subject`, `by-student`, `by-topic` and `by-plan` lookups.

## Dashboard (Sept 11)

- Replaced the placeholder Dashboard with the real one. A student selector at the top, then a grid of scored topic cards fetched from `GET /students/{id}/scores`, highest priority first.
- Each card shows the rank, subject, topic name, and three bars: priority out of 100, mastery percent and urgency percent, plus a one-line action hint.
- Priority above 70 is red "Urgent", 30 to 70 amber "Moderate", under 30 green "Strong". Same thresholds the scoring engine documents.
- Empty states for no students, no enrollments and a failed request, each with its own message rather than a blank grid.

## Study Plan page (Sept 12)

- The biggest page. Three stacked panels: a generate form (hours per day, number of days, start date), a plan picker listing the student's existing plans newest first, and the sessions of the selected plan grouped by day.
- Each session card shows topic, date, duration and a pending / done / missed toggle. Toggling updates optimistically and reverts with a message if the PATCH fails.
- A "Rebalance" button posts to `/agent/rebalance` with the manual trigger and shows the agent's explanation text above the refreshed sessions.
- Topic names come from a `topic_id → name` map built once from `/topics/` and topped up from the `topic_scores` returned by generation, so sessions never show bare UUIDs.
- Generate form validates ranges client-side (1 to 12 hours, 1 to 90 days) to mirror the backend's pydantic bounds.

## Frontend docs (Sept 14)

- Wrote `docs/frontend.md`: the route-to-file table, what each shared component and the hook do, the three ways `/api` reaches the backend, and the conventions we follow for state, errors and styling.
- Kept it to one page. Anyone who reads it and `api/client.js` can find their way around the rest.

## README and project index (Sept 14)

- Rewrote `README.md` and `docs/index.md` so both describe what the system does now, where each piece lives, and a two-line quick start. Added a team line with who owns what.
- Status table on the index lists every area and what is still not started, so nobody has to read the journals to know where we are.

## Next Steps

- Deploy: backend to Render, frontend to Vercel with `VITE_API_BASE` set.
- Link Dashboard cards to the study plan for that topic.
- Prototype-stage report.
