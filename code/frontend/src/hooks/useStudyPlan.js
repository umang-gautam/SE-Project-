import { useState, useEffect } from 'react';
import {
  fetchPlansByStudent,
  fetchSessionsByPlan,
  updateSession,
} from '../api/client.js';

/**
 * useStudyPlan — owns a student's plans, the selected plan and its sessions.
 *
 * Loads plans whenever `studentId` changes, selects the newest, and loads
 * its sessions. Exposes the setters too, because plan generation and the
 * rebalance agent replace sessions and plans from their own responses.
 */
export default function useStudyPlan(studentId) {
  const [studentPlans, setStudentPlans] = useState([]);
  const [selectedPlanId, setSelectedPlanId] = useState('');
  const [sessions, setSessions] = useState([]);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [sessionsError, setSessionsError] = useState(null);
  const [updatingSessionId, setUpdatingSessionId] = useState(null);

  const loadPlanSessions = async (planId) => {
    if (!planId) {
      setSessions([]);
      return;
    }
    setLoadingSessions(true);
    setSessionsError(null);
    try {
      const data = await fetchSessionsByPlan(planId);
      setSessions(Array.isArray(data) ? data : []);
    } catch (err) {
      setSessionsError(err.message || 'Failed to load study sessions.');
      setSessions([]);
    } finally {
      setLoadingSessions(false);
    }
  };

  const loadStudentPlans = async (id) => {
    if (!id) {
      setStudentPlans([]);
      setSelectedPlanId('');
      setSessions([]);
      return;
    }
    setLoadingSessions(true);
    setSessionsError(null);
    try {
      const plans = await fetchPlansByStudent(id);
      const list = Array.isArray(plans) ? plans : [];
      setStudentPlans(list);
      if (list.length > 0) {
        const sorted = [...list].sort(
          (a, b) => new Date(b.start_date || 0) - new Date(a.start_date || 0)
        );
        setSelectedPlanId(sorted[0].id);
        await loadPlanSessions(sorted[0].id);
      } else {
        setSelectedPlanId('');
        setSessions([]);
      }
    } catch (err) {
      setSessionsError(err.message || 'Failed to load study plans.');
      setSessions([]);
    } finally {
      setLoadingSessions(false);
    }
  };

  useEffect(() => {
    if (studentId) loadStudentPlans(studentId);
  }, [studentId]);

  const selectPlan = async (planId) => {
    setSelectedPlanId(planId);
    if (planId) {
      await loadPlanSessions(planId);
    } else {
      setSessions([]);
    }
  };

  /** Optimistic status change; reverts and reports if the PATCH fails. */
  const setSessionStatus = async (sessionId, newStatus) => {
    const current = sessions.find((s) => s.id === sessionId);
    if (!current || current.status === newStatus) return;
    const previousStatus = current.status;
    setSessions((prev) =>
      prev.map((s) => (s.id === sessionId ? { ...s, status: newStatus } : s))
    );
    setUpdatingSessionId(sessionId);
    try {
      await updateSession(sessionId, { status: newStatus });
    } catch (err) {
      setSessions((prev) =>
        prev.map((s) =>
          s.id === sessionId ? { ...s, status: previousStatus } : s
        )
      );
      alert(`Could not update session status: ${err.message}`);
    } finally {
      setUpdatingSessionId(null);
    }
  };

  return {
    studentPlans, setStudentPlans,
    selectedPlanId, setSelectedPlanId,
    sessions, setSessions,
    loadingSessions, sessionsError,
    loadPlanSessions, selectPlan,
    updatingSessionId, setSessionStatus,
  };
}
