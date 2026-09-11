import { useState, useEffect } from 'react';
import { fetchStudents, fetchStudentScores } from '../api/client.js';
import TopicCard from '../components/TopicCard.jsx';

/**
 * Dashboard Page Component
 */
export default function Dashboard() {
  const [students, setStudents] = useState([]);
  const [selectedStudentId, setSelectedStudentId] = useState('');
  const [scores, setScores] = useState([]);

  // Loading and error states
  const [loadingStudents, setLoadingStudents] = useState(true);
  const [studentsError, setStudentsError] = useState(null);
  const [loadingScores, setLoadingScores] = useState(false);
  const [scoresError, setScoresError] = useState(null);

  // Fetch all students on mount
  const loadStudents = async () => {
    setLoadingStudents(true);
    setStudentsError(null);
    try {
      const data = await fetchStudents();
      const list = Array.isArray(data) ? data : [];
      setStudents(list);

      // Auto-select the first student if available and none currently selected
      if (list.length > 0 && !selectedStudentId) {
        setSelectedStudentId(list[0].id);
      }
    } catch (err) {
      setStudentsError(err.message || 'Failed to load students list.');
    } finally {
      setLoadingStudents(false);
    }
  };

  useEffect(() => {
    loadStudents();
  }, []);

  // Fetch student scores whenever selected student changes
  const loadStudentScores = async (studentId) => {
    if (!studentId) {
      setScores([]);
      setScoresError(null);
      return;
    }

    setLoadingScores(true);
    setScoresError(null);
    try {
      const data = await fetchStudentScores(studentId);
      setScores(Array.isArray(data) ? data : []);
    } catch (err) {
      setScoresError(err.message || 'Failed to fetch topic scores for this student.');
    } finally {
      setLoadingScores(false);
    }
  };

  useEffect(() => {
    if (selectedStudentId) {
      loadStudentScores(selectedStudentId);
    } else {
      setScores([]);
      setScoresError(null);
    }
  }, [selectedStudentId]);

  // Sort scored topics by priority descending (highest priority = study first)
  const sortedScores = [...scores].sort(
    (a, b) => (Number(b.priority) || 0) - (Number(a.priority) || 0)
  );

  // Metrics summary
  const urgentCount = sortedScores.filter((t) => (Number(t.priority) || 0) > 70).length;
  const moderateCount = sortedScores.filter(
    (t) => (Number(t.priority) || 0) >= 30 && (Number(t.priority) || 0) <= 70
  ).length;
  const strongCount = sortedScores.filter((t) => (Number(t.priority) || 0) < 30).length;

  const selectedStudent = students.find((s) => s.id === selectedStudentId);

  return (
    <div className="space-y-6">
      {/* ── Page Header ────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-gray-200">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">
            Workload Dashboard
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Prioritized topic overview balancing mastery and upcoming deadline urgency.
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg border border-gray-200 shadow-sm text-xs">
          <span className="font-semibold text-gray-500 mr-1">Priority:</span>
          <span className="inline-flex items-center gap-1 font-medium text-red-700">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500" />
            &gt;70 Urgent
          </span>
          <span className="text-gray-300">|</span>
          <span className="inline-flex items-center gap-1 font-medium text-amber-700">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
            30-70 Moderate
          </span>
          <span className="text-gray-300">|</span>
          <span className="inline-flex items-center gap-1 font-medium text-emerald-700">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
            &lt;30 Strong
          </span>
        </div>
      </div>

      {/* ── Student Selector Card ──────────────────────────────── */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="w-full sm:max-w-md">
            <label
              htmlFor="student-select"
              className="block text-sm font-semibold text-gray-700 mb-1"
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
                  -- Select a student --
                </option>
                {students.map((student) => (
                  <option key={student.id} value={student.id}>
                    {student.name} {student.email ? `(${student.email})` : ''}
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Student Quick Info */}
          {selectedStudent && (
            <div className="text-sm text-gray-600 bg-gray-50 px-4 py-2 rounded-lg border border-gray-200">
              <span className="font-semibold text-gray-800">{selectedStudent.name}</span>
              {selectedStudent.email && (
                <span className="text-gray-500 block text-xs">{selectedStudent.email}</span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* ── Scored Topics Section ──────────────────────────────── */}
      {!selectedStudentId ? (
        <div className="bg-white rounded-xl border border-dashed border-gray-300 p-12 text-center">
          <div className="mx-auto w-12 h-12 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-600 mb-3 text-xl font-bold">
            👤
          </div>
          <h3 className="text-base font-semibold text-gray-900 mb-1">
            No Student Selected
          </h3>
          <p className="text-sm text-gray-500 max-w-sm mx-auto">
            Choose a student from the dropdown above to inspect their enrolled topics, mastery %, urgency %, and prioritized study queue.
          </p>
        </div>
      ) : loadingScores ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
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
          <p className="text-sm font-medium text-gray-700">
            Calculating topic priorities and urgency...
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Analyzing student performance records and assignment due dates
          </p>
        </div>
      ) : scoresError ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <div className="text-red-600 text-lg font-bold mb-1">Error Loading Scores</div>
          <p className="text-sm text-red-700 mb-4">{scoresError}</p>
          <button
            onClick={() => loadStudentScores(selectedStudentId)}
            className="inline-flex items-center px-4 py-2 text-sm font-semibold rounded-lg text-white bg-red-600 hover:bg-red-700 transition"
          >
            Retry Loading
          </button>
        </div>
      ) : sortedScores.length === 0 ? (
        <div className="bg-white rounded-xl border border-dashed border-gray-300 p-12 text-center">
          <div className="mx-auto w-12 h-12 rounded-full bg-amber-50 flex items-center justify-center text-amber-600 mb-3 text-xl font-bold">
            📚
          </div>
          <h3 className="text-base font-semibold text-gray-900 mb-1">
            No Scored Topics Found
          </h3>
          <p className="text-sm text-gray-500 max-w-md mx-auto">
            This student has no enrolled subjects or assigned topics yet. Enroll the student in subjects or add topics to generate prioritized workload scores.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Summary Stats Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Total Topics
              </span>
              <p className="text-2xl font-black text-gray-900 mt-1">
                {sortedScores.length}
              </p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-red-200 bg-red-50/30 shadow-sm">
              <span className="text-xs font-semibold text-red-600 uppercase tracking-wider">
                Urgent (&gt;70)
              </span>
              <p className="text-2xl font-black text-red-700 mt-1">
                {urgentCount}
              </p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-amber-200 bg-amber-50/30 shadow-sm">
              <span className="text-xs font-semibold text-amber-600 uppercase tracking-wider">
                Moderate (30-70)
              </span>
              <p className="text-2xl font-black text-amber-700 mt-1">
                {moderateCount}
              </p>
            </div>

            <div className="bg-white p-4 rounded-xl border border-emerald-200 bg-emerald-50/30 shadow-sm">
              <span className="text-xs font-semibold text-emerald-600 uppercase tracking-wider">
                Strong (&lt;30)
              </span>
              <p className="text-2xl font-black text-emerald-700 mt-1">
                {strongCount}
              </p>
            </div>
          </div>

          {/* Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 pt-2">
            {sortedScores.map((topic, index) => (
              <TopicCard
                key={topic.topic_id || topic.id || index}
                topic={topic}
                rank={index + 1}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
