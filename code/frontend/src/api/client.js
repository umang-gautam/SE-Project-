/**
 * API client — single source of truth for all backend calls.
 *
 * Every component imports from here instead of writing its own fetch().
 *
 * Base URL: VITE_API_BASE if set at build time, otherwise '/api', which the
 * Vite dev server and the nginx container both proxy to the backend. Set
 * VITE_API_BASE only for hosting where no proxy sits in front (e.g. a
 * static host talking to a separately deployed backend).
 */

const BASE = (import.meta.env.VITE_API_BASE || '/api').replace(/\/$/, '');

async function request(path, options = {}) {
  const url = `${BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });

  if (res.status === 204) return null; // DELETE returns no content

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || data.message || `Request failed: ${res.status}`);
  }

  return data;
}

// ── Students ────────────────────────────────────────────────
export const fetchStudents   = ()            => request('/students/');
export const fetchStudent    = (id)          => request(`/students/${id}`);
export const createStudent   = (body)        => request('/students/', { method: 'POST', body: JSON.stringify(body) });
export const updateStudent   = (id, body)    => request(`/students/${id}`, { method: 'PATCH', body: JSON.stringify(body) });
export const deleteStudent   = (id)          => request(`/students/${id}`, { method: 'DELETE' });
export const fetchStudentScores = (id)       => request(`/students/${id}/scores`);

// ── Subjects ────────────────────────────────────────────────
export const fetchSubjects   = ()            => request('/subjects/');
export const fetchSubject    = (id)          => request(`/subjects/${id}`);
export const createSubject   = (body)        => request('/subjects/', { method: 'POST', body: JSON.stringify(body) });
export const updateSubject   = (id, body)    => request(`/subjects/${id}`, { method: 'PATCH', body: JSON.stringify(body) });
export const deleteSubject   = (id)          => request(`/subjects/${id}`, { method: 'DELETE' });

// ── Topics ──────────────────────────────────────────────────
export const fetchTopics        = ()         => request('/topics/');
export const fetchTopicsBySubject = (subId)  => request(`/topics/by-subject/${subId}`);
export const createTopic        = (body)     => request('/topics/', { method: 'POST', body: JSON.stringify(body) });
export const deleteTopic        = (id)       => request(`/topics/${id}`, { method: 'DELETE' });

// ── Assignments ─────────────────────────────────────────────
export const fetchAssignments       = ()        => request('/assignments/');
export const fetchAssignmentsByTopic = (topicId) => request(`/assignments/by-topic/${topicId}`);
export const createAssignment       = (body)    => request('/assignments/', { method: 'POST', body: JSON.stringify(body) });
export const deleteAssignment       = (id)      => request(`/assignments/${id}`, { method: 'DELETE' });

// ── Enrollments ─────────────────────────────────────────────
export const fetchEnrollments          = ()       => request('/enrollments/');
export const fetchEnrollmentsByStudent = (stuId)  => request(`/enrollments/by-student/${stuId}`);
export const createEnrollment          = (body)   => request('/enrollments/', { method: 'POST', body: JSON.stringify(body) });
export const deleteEnrollment          = (id)     => request(`/enrollments/${id}`, { method: 'DELETE' });

// ── Performance ─────────────────────────────────────────────
export const createPerformanceRecord = (body) => request('/performance/', { method: 'POST', body: JSON.stringify(body) });
export const fetchPerformanceByStudent = (stuId) => request(`/performance/by-student/${stuId}`);

// ── Study Plans ─────────────────────────────────────────────
export const generatePlan    = (body)        => request('/study-plans/generate', { method: 'POST', body: JSON.stringify(body) });
export const fetchPlan       = (id)          => request(`/study-plans/${id}`);
export const fetchPlansByStudent = (stuId)   => request(`/study-plans/by-student/${stuId}`);

// ── Study Sessions ──────────────────────────────────────────
export const fetchSessionsByPlan = (planId)  => request(`/study-sessions/by-plan/${planId}`);
export const updateSession       = (id, body) => request(`/study-sessions/${id}`, { method: 'PATCH', body: JSON.stringify(body) });

// ── Agent ───────────────────────────────────────────────────
export const triggerRebalance = (body) => request('/agent/rebalance', { method: 'POST', body: JSON.stringify(body) });
