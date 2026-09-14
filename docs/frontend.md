# Frontend

React 19, Vite 6, Tailwind 3, react-router 7. Lives in `code/frontend`.

## Pages

| Route | File | What it does |
|---|---|---|
| `/` | `pages/Dashboard.jsx` | Pick a student, see their topics as priority-ranked cards |
| `/subjects` | `pages/Subjects.jsx` | Create and delete subjects, expand one to manage its topics |
| `/performance` | `pages/PerformanceEntry.jsx` | Log a score per topic, browse the score history |
| `/study-plan` | `pages/StudyPlanView.jsx` | Generate a plan, view sessions by day, toggle status, trigger the agent |

## Shared pieces

- `components/TopicCard.jsx`: one scored topic with priority, mastery and urgency bars. Red above 70, amber from 30, green below.
- `components/ScoreBadge.jsx`: a score pill. Green at 80+, yellow at 50+, red below.
- `components/SessionBlock.jsx`: one study session with its pending / done / missed toggle.
- `hooks/useStudyPlan.js`: plans, selected plan, sessions and the optimistic status update for a student.
- `api/client.js`: the only place `fetch` is called. One function per endpoint.

## Talking to the backend

Every request goes to `/api/...`.

- `npm run dev`: Vite proxies `/api` to `http://127.0.0.1:8000`.
- Docker: nginx proxies `/api/` to the `backend` service.
- Hosted separately: set `VITE_API_BASE` at build time (see `.env.example`).

The client never needs to know which of the three it is running under.

## Conventions

- Pages own their state with `useState` and `useEffect`. No global store; nothing is shared across pages except the selected student, which each page asks for.
- Every async action has its own loading and error state, keyed by id when the action is per-row. A failed request shows the backend's message verbatim next to the thing that failed.
- Status changes are optimistic and revert on failure.
- Styling is Tailwind utility classes in JSX. No CSS files besides `index.css` with the three Tailwind directives.

## Commands

```sh
npm install
npm run dev        # http://localhost:5173
npm run build      # dist/
npm run preview    # serve dist/ locally
```
