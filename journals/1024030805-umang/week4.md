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
