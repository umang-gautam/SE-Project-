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
