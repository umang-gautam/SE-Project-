# Vriti's Journal

Roll No. 1024030801

Name: Vriti

Frontend track, working alongside Umang on the React app under `code/frontend`.

---

## 2026-09-09 — Subjects & Topics page

### What I did
- Replaced the placeholder `pages/Subjects.jsx` with the real page: list subjects, create one from a name and code, expand a subject to load its topics, add and delete topics, delete a subject.
- Every async action has its own loading and error state, keyed by subject id where the action is per-subject, so one failing request never greys out the whole page.
- Delete asks for confirmation first, since it cascades to topics on the backend.

### Decisions
- Topics load lazily on expand, not with the subject list. A student with ten subjects should not wait on ten extra requests to see the page.
- Success and failure feedback is one shared banner that clears itself, instead of toasts, which would need a dependency.

### Next
- Performance entry page.

---

## 2026-09-10 — Performance entry page

### What I did
- Replaced the placeholder `pages/PerformanceEntry.jsx`. Pick a student, see every topic they are enrolled in with its current priority, type a score per topic and submit. Below that, the student's full score history with a colour-coded badge: green at 80 and above, yellow from 50, red below.
- Scores are validated client-side to 0 to 100 before the request, and the backend's 422 message is shown verbatim if it disagrees.
- After a successful submit the topic list re-fetches its scores, so the priority number on the same row updates without a page reload.

### Decisions
- Score inputs are keyed by topic id in one state object rather than one state per input. Twenty topics should not mean twenty `useState` calls.
- The badge is inline for now. It belongs in `components/` once a second page needs it.

### Next
- Pull the badge and the topic card out into shared components.
