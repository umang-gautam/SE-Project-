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
