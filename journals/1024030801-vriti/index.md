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

---

## 2026-09-11 — Shared components: ScoreBadge and TopicCard

### What I did
- Moved `ScoreBadge` out of `PerformanceEntry.jsx` into `components/ScoreBadge.jsx` and `TopicScoreCard` (with its `getPriorityMeta` colour helper) out of `Dashboard.jsx` into `components/TopicCard.jsx`. The pages import them; behaviour and markup are unchanged.
- This fills in two of the three component files the blueprint lists under `src/components/`.

### Decisions
- Pure move, no API changes, so the diff is reviewable as "cut here, paste there". Any tweak to the card's look is a separate commit.
- `getPriorityMeta` stays private to `TopicCard`. Nothing else needs the colour tokens yet; exporting them now is guessing.

### Next
- `SessionBlock` from the study plan page, once Umang lands it.

---

## 2026-09-12 — Shared component: SessionBlock

### What I did
- Moved `SessionCard` and its `getStatusBadgeConfig` helper out of `StudyPlanView.jsx` into `components/SessionBlock.jsx`, the name the blueprint uses. Props are unchanged: `session`, `topicName`, `isUpdating`, `onStatusChange`.
- All three blueprint components now exist as real files. `StudyPlanView.jsx` drops by about 115 lines.

### Decisions
- Kept the status toggle inside the block rather than lifting it to the page. The block already receives `onStatusChange`; the page should not know what buttons exist.

### Next
- Pull the plan and session loading logic out of the page into `hooks/useStudyPlan.js`.

---

## 2026-09-13 — useStudyPlan hook

### What I did
- Added `hooks/useStudyPlan.js`. Given a student id it owns the plan list, the selected plan, its sessions, the loading and error flags, and the optimistic status toggle. It reloads plans whenever the student changes and picks the newest.
- `StudyPlanView.jsx` now destructures the hook and keeps only what is page-specific: the generate form, the rebalance panel and the topic-name map. The page lost roughly 130 more lines; the JSX did not change because the hook's values are destructured under the names the JSX already used.
- The hook exposes its setters on purpose. Generation and rebalance both replace sessions and plans from their own responses.

### Decisions
- One hook, not three. Plans, selected plan and sessions are one piece of state that changes together; separate hooks would need to coordinate through the page.
- Left `alert()` in the status-revert path as it was. Replacing it with an in-page message is a behaviour change for another commit.

### Next
- Environment-driven API base URL for deployments without the Vite proxy.
