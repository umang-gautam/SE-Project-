import { useState, useEffect, useMemo } from 'react';
import {
  fetchStudents,
  generatePlan,
  fetchPlansByStudent,
  triggerRebalance,
  fetchTopics,
} from '../api/client.js';
import SessionBlock from '../components/SessionBlock.jsx';
import useStudyPlan from '../hooks/useStudyPlan.js';

/**
 * Returns today's date formatted as YYYY-MM-DD in local time.
 */
function getTodayString() {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const day = String(today.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Formats a date string (YYYY-MM-DD) into a human-readable header.
 */
function formatDateHeading(dateStr) {
  if (!dateStr) return '';
  try {
    const [year, month, day] = dateStr.split('-').map(Number);
    const dateObj = new Date(year, month - 1, day);
    return dateObj.toLocaleDateString(undefined, {
      weekday: 'long',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

/**
 * Main Study Plan View page
 */
export default function StudyPlanView() {
  // ── Student selection state ──────────────────────────────────────────
  const [students, setStudents] = useState([]);
  const [selectedStudentId, setSelectedStudentId] = useState('');
  const [loadingStudents, setLoadingStudents] = useState(false);
  const [studentsError, setStudentsError] = useState(null);

  // ── Topic metadata mapping (topic_id -> topic_name) ───────────────────
  const [topicMap, setTopicMap] = useState({});

  // ── Plan generation form state ───────────────────────────────────────
  const [hoursPerDay, setHoursPerDay] = useState(2);
  const [numDays, setNumDays] = useState(7);
  const [startDate, setStartDate] = useState(getTodayString());
  const [generatingPlan, setGeneratingPlan] = useState(false);
  const [generationError, setGenerationError] = useState(null);

  // ── Plans, selected plan, sessions and status updates (hook) ────────
  const {
    studentPlans, setStudentPlans,
    selectedPlanId, setSelectedPlanId,
    sessions, setSessions,
    loadingSessions, sessionsError,
    loadPlanSessions, selectPlan: handlePlanSelectChange,
    updatingSessionId, setSessionStatus: handleStatusChange,
  } = useStudyPlan(selectedStudentId);

  // ── Rebalance state ──────────────────────────────────────────────────
  const [isRebalancing, setIsRebalancing] = useState(false);
  const [rebalanceError, setRebalanceError] = useState(null);
  const [agentExplanation, setAgentExplanation] = useState(null);

  // ── 1. Initial load: Students and Topic registry ─────────────────────
  const loadStudents = async () => {
    setLoadingStudents(true);
    setStudentsError(null);
    try {
      const data = await fetchStudents();
      const list = Array.isArray(data) ? data : [];
      setStudents(list);
      if (list.length > 0 && !selectedStudentId) {
        setSelectedStudentId(list[0].id);
      }
    } catch (err) {
      setStudentsError(err.message || 'Failed to load students list.');
    } finally {
      setLoadingStudents(false);
    }
  };

  const loadTopics = async () => {
    try {
      const data = await fetchTopics();
      if (Array.isArray(data)) {
        const map = {};
        data.forEach((t) => {
          map[t.id] = t.name;
        });
        setTopicMap((prev) => ({ ...prev, ...map }));
      }
    } catch {
      // Topics lookup failure is non-fatal; sessions still show topic_id as fallback
    }
  };

  useEffect(() => {
    loadStudents();
    loadTopics();
  }, []);

  // ── 2. Clear per-student messages when the selection changes ────────
  useEffect(() => {
    if (selectedStudentId) {
      setAgentExplanation(null);
      setGenerationError(null);
      setRebalanceError(null);
    }
  }, [selectedStudentId]);

  // ── 4. Plan Generation Form Submit ───────────────────────────────────
  const handleGeneratePlan = async (e) => {
    e.preventDefault();

    if (!selectedStudentId) {
      setGenerationError('Please select a student first.');
      return;
    }

    const hours = Number(hoursPerDay);
    const days = Number(numDays);

    if (isNaN(hours) || hours < 1 || hours > 12) {
      setGenerationError('Daily study hours must be between 1 and 12.');
      return;
    }

    if (isNaN(days) || days < 1 || days > 90) {
      setGenerationError('Number of days must be between 1 and 90.');
      return;
    }

    setGeneratingPlan(true);
    setGenerationError(null);

    try {
      const payload = {
        student_id: selectedStudentId,
        hours_per_day: hours,
        num_days: days,
        start_date: startDate || getTodayString(),
      };

      const result = await generatePlan(payload);

      // Save any topic names returned from scoring in our mapping
      if (Array.isArray(result.topic_scores)) {
        const newMap = {};
        result.topic_scores.forEach((ts) => {
          if (ts.topic_id && ts.topic_name) {
            newMap[ts.topic_id] = ts.topic_name;
          }
        });
        setTopicMap((prev) => ({ ...prev, ...newMap }));
      }

      // Update sessions & current plan id
      const generatedSessions = Array.isArray(result.sessions)
        ? result.sessions
        : [];
      setSessions(generatedSessions);
      setSelectedPlanId(result.plan_id);

      // Refresh student plans list so dropdown stays current
      const refreshedPlans = await fetchPlansByStudent(selectedStudentId);
      setStudentPlans(Array.isArray(refreshedPlans) ? refreshedPlans : []);
    } catch (err) {
      setGenerationError(err.message || 'Failed to generate study plan.');
    } finally {
      setGeneratingPlan(false);
    }
  };

  // ── 6. Rebalance Button (calls triggerRebalance) ──────────────────────
  const handleRebalance = async () => {
    if (!selectedStudentId) {
      setRebalanceError('Please select a student to rebalance.');
      return;
    }

    setIsRebalancing(true);
    setRebalanceError(null);

    try {
      const response = await triggerRebalance({
        student_id: selectedStudentId,
        trigger: 'manual',
      });

      // Show agent's explanation
      setAgentExplanation({
        text: response.explanation || 'Rebalance completed.',
        changesNeeded: response.changes_needed,
        trigger: response.trigger,
      });

      // If a new plan was produced, update active plan & sessions
      if (response.new_plan) {
        if (response.new_plan.plan_id) {
          setSelectedPlanId(response.new_plan.plan_id);
        }
        if (Array.isArray(response.new_plan.sessions)) {
          setSessions(response.new_plan.sessions);
        }
        if (Array.isArray(response.new_plan.topic_scores)) {
          const newMap = {};
          response.new_plan.topic_scores.forEach((ts) => {
            if (ts.topic_id && ts.topic_name) {
              newMap[ts.topic_id] = ts.topic_name;
            }
          });
          setTopicMap((prev) => ({ ...prev, ...newMap }));
        }

        // Refresh plans list
        const refreshedPlans = await fetchPlansByStudent(selectedStudentId);
        setStudentPlans(Array.isArray(refreshedPlans) ? refreshedPlans : []);
      }
    } catch (err) {
      setRebalanceError(err.message || 'Failed to trigger rebalance.');
    } finally {
      setIsRebalancing(false);
    }
  };

  // ── 7. Group sessions by date ────────────────────────────────────────
  const groupedSessions = useMemo(() => {
    if (!sessions || sessions.length === 0) return {};

    // Sort all sessions by date ascending
    const sorted = [...sessions].sort(
      (a, b) => new Date(a.date) - new Date(b.date)
    );

    const groups = {};
    for (const session of sorted) {
      const d = session.date || 'Undated';
      if (!groups[d]) {
        groups[d] = [];
      }
      groups[d].push(session);
    }
    return groups;
  }, [sessions]);

  const sortedDates = useMemo(() => {
    return Object.keys(groupedSessions).sort((a, b) => new Date(a) - new Date(b));
  }, [groupedSessions]);

  const selectedStudent = students.find((s) => s.id === selectedStudentId);

  return (
    <div className="space-y-8 pb-12">
      {/* ── Page Header ────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-gray-200">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">
            Study Plan Manager
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Generate customized study schedules and adapt dynamically using the AI rebalancing agent.
          </p>
        </div>

        {/* Status badges legend */}
        <div className="flex items-center gap-3 bg-white px-3.5 py-2 rounded-xl border border-gray-200 shadow-sm text-xs">
          <span className="font-semibold text-gray-500">Status:</span>
          <span className="inline-flex items-center gap-1.5 font-medium text-blue-700">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
            Pending
          </span>
          <span className="text-gray-300">|</span>
          <span className="inline-flex items-center gap-1.5 font-medium text-green-700">
            <span className="w-2.5 h-2.5 rounded-full bg-green-500" />
            Done
          </span>
          <span className="text-gray-300">|</span>
          <span className="inline-flex items-center gap-1.5 font-medium text-red-700">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500" />
            Missed
          </span>
        </div>
      </div>

      {/* ── Top Controls: Student Selector & Rebalance Action ─────── */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
          {/* 1. Student selector */}
          <div className="w-full md:max-w-md">
            <label
              htmlFor="student-select"
              className="block text-sm font-semibold text-gray-700 mb-1.5"
            >
              Select Student
            </label>

            {loadingStudents ? (
              <div className="flex items-center gap-2 text-sm text-gray-500 py-2">
                <svg
                  className="animate-spin h-4 w-4 text-indigo-600"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v8H4z"
                  />
                </svg>
                <span>Loading students...</span>
              </div>
            ) : studentsError ? (
              <div className="text-sm text-red-600 flex items-center gap-2">
                <span>{studentsError}</span>
                <button
                  onClick={loadStudents}
                  className="text-xs text-indigo-600 underline hover:text-indigo-800 font-semibold"
                >
                  Retry
                </button>
              </div>
            ) : (
              <select
                id="student-select"
                value={selectedStudentId}
                onChange={(e) => setSelectedStudentId(e.target.value)}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="" disabled>
                  -- Choose a student --
                </option>
                {students.map((stu) => (
                  <option key={stu.id} value={stu.id}>
                    {stu.name} ({stu.email})
                  </option>
                ))}
              </select>
            )}

            {selectedStudent && (
              <p className="text-xs text-gray-500 mt-1.5">
                Active student: <span className="font-semibold text-gray-700">{selectedStudent.name}</span>
              </p>
            )}
          </div>

          {/* 7. Rebalance Button */}
          <div className="flex flex-col items-start md:items-end gap-1">
            <button
              type="button"
              disabled={!selectedStudentId || isRebalancing}
              onClick={handleRebalance}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-bold text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 shadow-sm hover:shadow transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
            >
              {isRebalancing ? (
                <>
                  <svg
                    className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                    viewBox="0 0 24 24"
                    fill="none"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8v8H4z"
                    />
                  </svg>
                  Rebalancing with AI...
                </>
              ) : (
                <>
                  <svg
                    className="w-4 h-4 text-indigo-200"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                    />
                  </svg>
                  Rebalance Plan
                </>
              )}
            </button>
            <span className="text-[11px] text-gray-500">
              Evaluates missed sessions & priorities to adapt plan
            </span>
          </div>
        </div>

        {/* Rebalance Error Message */}
        {rebalanceError && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center justify-between">
            <span>{rebalanceError}</span>
            <button
              onClick={() => setRebalanceError(null)}
              className="text-red-500 hover:text-red-700 font-bold ml-2"
            >
              ✕
            </button>
          </div>
        )}

        {/* Agent's Explanation Banner */}
        {agentExplanation && (
          <div className="mt-5 p-4 rounded-xl border bg-indigo-50/70 border-indigo-200 text-sm">
            <div className="flex items-center justify-between gap-2 mb-2">
              <div className="flex items-center gap-2">
                <span className="p-1 rounded-md bg-indigo-600 text-white">
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                </span>
                <h3 className="font-bold text-indigo-950">
                  Agent Reasoning &amp; Decision
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border ${
                    agentExplanation.changesNeeded
                      ? 'bg-green-100 text-green-800 border-green-200'
                      : 'bg-gray-100 text-gray-700 border-gray-200'
                  }`}
                >
                  {agentExplanation.changesNeeded
                    ? 'Plan Updated'
                    : 'No Changes Needed'}
                </span>
                <button
                  type="button"
                  onClick={() => setAgentExplanation(null)}
                  className="text-gray-400 hover:text-gray-600 font-bold text-xs p-1"
                  title="Dismiss explanation"
                >
                  ✕
                </button>
              </div>
            </div>
            <pre className="whitespace-pre-wrap font-sans text-xs sm:text-sm text-indigo-900 bg-white/80 p-3 rounded-lg border border-indigo-100 leading-relaxed overflow-x-auto">
              {agentExplanation.text}
            </pre>
          </div>
        )}
      </div>

      {/* ── 2 & 3: Plan Generation Form ────────────────────────────── */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <div className="mb-4">
          <h2 className="text-lg font-bold text-gray-900">
            Generate Study Plan
          </h2>
          <p className="text-xs text-gray-500">
            Set your daily availability and timeframe. The planner allocates time to topics proportionally to their priority score.
          </p>
        </div>

        {generationError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center justify-between">
            <span>{generationError}</span>
            <button
              onClick={() => setGenerationError(null)}
              className="text-red-500 hover:text-red-700 font-bold ml-2"
            >
              ✕
            </button>
          </div>
        )}

        <form onSubmit={handleGeneratePlan}>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
            {/* hours_per_day */}
            <div>
              <label
                htmlFor="hours-per-day"
                className="block text-xs font-semibold text-gray-700 mb-1"
              >
                Hours Per Day (1 – 12)
              </label>
              <input
                id="hours-per-day"
                type="number"
                min="1"
                max="12"
                step="0.5"
                required
                value={hoursPerDay}
                onChange={(e) => setHoursPerDay(e.target.value)}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
              <span className="text-[11px] text-gray-400 mt-1 block">
                Recommended: 2 – 4 hours
              </span>
            </div>

            {/* num_days */}
            <div>
              <label
                htmlFor="num-days"
                className="block text-xs font-semibold text-gray-700 mb-1"
              >
                Number of Days (1 – 90)
              </label>
              <input
                id="num-days"
                type="number"
                min="1"
                max="90"
                step="1"
                required
                value={numDays}
                onChange={(e) => setNumDays(e.target.value)}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
              <span className="text-[11px] text-gray-400 mt-1 block">
                e.g. 7 days (weekly sprint)
              </span>
            </div>

            {/* start_date */}
            <div>
              <label
                htmlFor="start-date"
                className="block text-xs font-semibold text-gray-700 mb-1"
              >
                Start Date
              </label>
              <input
                id="start-date"
                type="date"
                required
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
              <span className="text-[11px] text-gray-400 mt-1 block">
                Defaults to today
              </span>
            </div>
          </div>

          <div className="flex items-center justify-end">
            <button
              type="submit"
              disabled={generatingPlan || !selectedStudentId}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm hover:shadow transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
            >
              {generatingPlan ? (
                <>
                  <svg
                    className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                    viewBox="0 0 24 24"
                    fill="none"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8v8H4z"
                    />
                  </svg>
                  Generating Plan...
                </>
              ) : (
                <>
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                    />
                  </svg>
                  Generate Plan
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* ── 4 & 5: Generated Plan & Grouped Sessions Display ────────── */}
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h2 className="text-xl font-bold text-gray-900">
              Scheduled Study Sessions
            </h2>
            <p className="text-xs text-gray-500">
              Review and track your daily sessions. Mark status as pending, done, or missed.
            </p>
          </div>

          {/* Plan selector if student has multiple plans */}
          {studentPlans.length > 1 && (
            <div className="flex items-center gap-2">
              <label
                htmlFor="plan-selector"
                className="text-xs font-semibold text-gray-600 whitespace-nowrap"
              >
                Plan History:
              </label>
              <select
                id="plan-selector"
                value={selectedPlanId}
                onChange={(e) => handlePlanSelectChange(e.target.value)}
                className="rounded-md border border-gray-300 bg-white px-2.5 py-1 text-xs text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-none"
              >
                {studentPlans.map((p, idx) => (
                  <option key={p.id} value={p.id}>
                    {idx === 0 ? 'Current: ' : 'Previous: '}
                    {p.start_date} to {p.end_date}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Loading sessions indicator */}
        {loadingSessions && (
          <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center shadow-sm">
            <svg
              className="animate-spin h-8 w-8 text-indigo-600 mx-auto mb-3"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v8H4z"
              />
            </svg>
            <p className="text-sm font-medium text-gray-600">
              Loading study sessions...
            </p>
          </div>
        )}

        {/* Sessions Error State */}
        {!loadingSessions && sessionsError && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-5 text-sm text-red-700 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <svg
                className="w-5 h-5 text-red-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span>{sessionsError}</span>
            </div>
            {selectedPlanId && (
              <button
                onClick={() => loadPlanSessions(selectedPlanId)}
                className="text-xs font-bold text-red-700 underline hover:text-red-900"
              >
                Retry
              </button>
            )}
          </div>
        )}

        {/* Empty state: No student selected */}
        {!loadingSessions && !selectedStudentId && (
          <div className="bg-white rounded-2xl border border-dashed border-gray-300 p-12 text-center">
            <svg
              className="w-12 h-12 text-gray-300 mx-auto mb-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="1.5"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
            <h3 className="text-base font-bold text-gray-800">
              No Student Selected
            </h3>
            <p className="text-xs text-gray-500 mt-1 max-w-sm mx-auto">
              Please choose a student from the dropdown above to view or create their study plan.
            </p>
          </div>
        )}

        {/* Empty state: Student selected but no sessions exist */}
        {!loadingSessions &&
          !sessionsError &&
          selectedStudentId &&
          sessions.length === 0 && (
            <div className="bg-white rounded-2xl border border-dashed border-gray-300 p-12 text-center">
              <div className="w-12 h-12 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto mb-3">
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <h3 className="text-base font-bold text-gray-800">
                No Study Plan Found
              </h3>
              <p className="text-xs text-gray-500 mt-1 max-w-md mx-auto mb-4">
                This student does not have any active study sessions yet. Use the form above to generate a balanced plan!
              </p>
            </div>
          )}

        {/* Grouped sessions timeline view */}
        {!loadingSessions && !sessionsError && sessions.length > 0 && (
          <div className="space-y-8">
            {sortedDates.map((dateStr) => {
              const daySessions = groupedSessions[dateStr] || [];
              const totalMinutes = daySessions.reduce(
                (sum, s) => sum + (Number(s.duration_minutes) || 0),
                0
              );

              return (
                <div
                  key={dateStr}
                  className="bg-gray-50/70 border border-gray-200/80 rounded-2xl p-5"
                >
                  {/* Date Group Header */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 mb-4 border-b border-gray-200 gap-2">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shadow-sm">
                        {dateStr.split('-')[2] || 'D'}
                      </div>
                      <div>
                        <h3 className="text-sm sm:text-base font-extrabold text-gray-900">
                          {formatDateHeading(dateStr)}
                        </h3>
                        <span className="text-[11px] text-gray-500">
                          {dateStr}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-white border border-gray-200 text-gray-700 shadow-sm">
                        {daySessions.length}{' '}
                        {daySessions.length === 1 ? 'session' : 'sessions'}
                      </span>
                      <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-indigo-50 border border-indigo-200 text-indigo-800">
                        {totalMinutes} min total
                      </span>
                    </div>
                  </div>

                  {/* Sessions grid for this date */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {daySessions.map((session) => {
                      const topicName =
                        topicMap[session.topic_id] ||
                        session.topic_name ||
                        `Topic: ${session.topic_id.slice(0, 8)}...`;

                      return (
                        <SessionBlock
                          key={session.id}
                          session={session}
                          topicName={topicName}
                          isUpdating={updatingSessionId === session.id}
                          onStatusChange={handleStatusChange}
                        />
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
