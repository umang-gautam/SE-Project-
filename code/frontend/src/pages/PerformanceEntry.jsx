import { useState, useEffect } from 'react';
import {
  fetchStudents,
  fetchStudentScores,
  createPerformanceRecord,
  fetchPerformanceByStudent,
} from '../api/client.js';
import ScoreBadge from '../components/ScoreBadge.jsx';

export default function PerformanceEntry() {
  // ── State ─────────────────────────────────────────────────────────────
  const [students, setStudents] = useState([]);
  const [selectedStudentId, setSelectedStudentId] = useState('');

  // Data for the selected student
  const [topics, setTopics] = useState([]);
  const [records, setRecords] = useState([]);

  // Loading states
  const [loadingStudents, setLoadingStudents] = useState(true);
  const [loadingStudentData, setLoadingStudentData] = useState(false);
  const [submittingTopicId, setSubmittingTopicId] = useState(null);

  // Error & notification states
  const [studentError, setStudentError] = useState(null);
  const [dataError, setDataError] = useState(null);
  const [recordError, setRecordError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // Per-topic score inputs: { [topicId]: string }
  const [scoreInputs, setScoreInputs] = useState({});

  // ── Fetch students on mount ───────────────────────────────────────────
  useEffect(() => {
    async function loadStudents() {
      setLoadingStudents(true);
      setStudentError(null);
      try {
        const data = await fetchStudents();
        setStudents(data || []);
      } catch (err) {
        setStudentError(err.message || 'Failed to load students.');
      } finally {
        setLoadingStudents(false);
      }
    }

    loadStudents();
  }, []);

  // ── Fetch student scores and performance records when student changes ─
  useEffect(() => {
    if (!selectedStudentId) {
      setTopics([]);
      setRecords([]);
      setScoreInputs({});
      setDataError(null);
      setRecordError(null);
      setSuccessMessage(null);
      return;
    }

    async function loadStudentData() {
      setLoadingStudentData(true);
      setDataError(null);
      setRecordError(null);
      setSuccessMessage(null);

      try {
        const [scoresData, recordsData] = await Promise.all([
          fetchStudentScores(selectedStudentId),
          fetchPerformanceByStudent(selectedStudentId),
        ]);

        setTopics(scoresData || []);
        setRecords(recordsData || []);
      } catch (err) {
        setDataError(err.message || 'Failed to load student data.');
      } finally {
        setLoadingStudentData(false);
      }
    }

    loadStudentData();
  }, [selectedStudentId]);

  // ── Score input change handler ────────────────────────────────────────
  function handleScoreChange(topicId, value) {
    setScoreInputs((prev) => ({
      ...prev,
      [topicId]: value,
    }));
    // Clear errors when user types
    if (recordError) setRecordError(null);
  }

  // ── Record score submission ───────────────────────────────────────────
  async function handleRecordScore(topic) {
    const rawScore = scoreInputs[topic.topic_id];

    if (rawScore === undefined || rawScore === null || rawScore.trim() === '') {
      setRecordError(`Please enter a score for "${topic.topic_name}".`);
      return;
    }

    const numScore = parseFloat(rawScore);
    if (isNaN(numScore) || numScore < 0 || numScore > 100) {
      setRecordError('Score must be a number between 0 and 100.');
      return;
    }

    setSubmittingTopicId(topic.topic_id);
    setRecordError(null);
    setSuccessMessage(null);

    try {
      await createPerformanceRecord({
        student_id: selectedStudentId,
        topic_id: topic.topic_id,
        score: numScore,
      });

      // Clear input on success
      setScoreInputs((prev) => ({
        ...prev,
        [topic.topic_id]: '',
      }));

      setSuccessMessage(
        `Successfully recorded score of ${numScore}% for ${topic.topic_name}!`
      );

      // Refresh records and topic scores
      const [updatedScores, updatedRecords] = await Promise.all([
        fetchStudentScores(selectedStudentId),
        fetchPerformanceByStudent(selectedStudentId),
      ]);
      setTopics(updatedScores || []);
      setRecords(updatedRecords || []);
    } catch (err) {
      setRecordError(err.message || 'Failed to record score.');
    } finally {
      setSubmittingTopicId(null);
    }
  }

  // ── Helper: Map topic_id to topic_name ─────────────────────────────────
  const topicNameMap = topics.reduce((acc, t) => {
    acc[t.topic_id] = t.topic_name;
    return acc;
  }, {});

  // ── Helper: Group topics by subject name ───────────────────────────────
  const topicsBySubject = topics.reduce((acc, topic) => {
    const subName = topic.subject_name || 'General Subject';
    if (!acc[subName]) acc[subName] = [];
    acc[subName].push(topic);
    return acc;
  }, {});

  // ── Format ISO date ───────────────────────────────────────────────────
  function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      return d.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  }

  return (
    <div className="space-y-8">
      {/* ── Page Header ─────────────────────────────────────────────── */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
          Performance Entry
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Record test and quiz scores for students to update mastery levels and optimize study schedules.
        </p>
      </div>

      {/* ── Student Selector ────────────────────────────────────────── */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <label
          htmlFor="student-select"
          className="block text-sm font-semibold text-gray-700 mb-2"
        >
          Select Student
        </label>

        {loadingStudents ? (
          <div className="flex items-center space-x-2 text-sm text-gray-500 py-2">
            <svg
              className="animate-spin h-5 w-5 text-indigo-600"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
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
        ) : studentError ? (
          <div className="rounded-md bg-red-50 p-4 border border-red-200">
            <p className="text-sm font-medium text-red-800">{studentError}</p>
          </div>
        ) : (
          <div className="max-w-md">
            <select
              id="student-select"
              value={selectedStudentId}
              onChange={(e) => setSelectedStudentId(e.target.value)}
              className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-800"
            >
              <option value="">-- Choose a student --</option>
              {students.map((student) => (
                <option key={student.id} value={student.id}>
                  {student.name} ({student.email})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* ── Notification Banners ────────────────────────────────────── */}
      {recordError && (
        <div className="rounded-lg bg-red-50 p-4 border border-red-200 flex items-start space-x-3">
          <span className="text-red-600 font-bold">✕</span>
          <div className="text-sm text-red-700">{recordError}</div>
        </div>
      )}

      {successMessage && (
        <div className="rounded-lg bg-green-50 p-4 border border-green-200 flex items-start space-x-3">
          <span className="text-green-600 font-bold">✓</span>
          <div className="text-sm text-green-700">{successMessage}</div>
        </div>
      )}

      {/* ── Topic Scoring Section ───────────────────────────────────── */}
      {selectedStudentId && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 space-y-6">
          <div className="border-b border-gray-200 pb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Enrolled Subjects & Topics
            </h2>
            <p className="text-sm text-gray-500 mt-0.5">
              Enter quiz or test scores (0–100) to update mastery for each topic.
            </p>
          </div>

          {loadingStudentData ? (
            <div className="flex items-center justify-center space-x-2 py-12 text-sm text-gray-500">
              <svg
                className="animate-spin h-6 w-6 text-indigo-600"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
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
              <span>Loading enrolled topics and performance...</span>
            </div>
          ) : dataError ? (
            <div className="rounded-md bg-red-50 p-4 border border-red-200">
              <p className="text-sm font-medium text-red-800">{dataError}</p>
            </div>
          ) : topics.length === 0 ? (
            <div className="text-center py-8 text-sm text-gray-500">
              No enrolled subjects or topics found for this student.
            </div>
          ) : (
            <div className="space-y-6">
              {Object.entries(topicsBySubject).map(([subjectName, subjectTopics]) => (
                <div
                  key={subjectName}
                  className="border border-gray-100 rounded-lg bg-gray-50/50 p-4"
                >
                  <h3 className="text-sm font-bold uppercase tracking-wider text-indigo-700 mb-3">
                    {subjectName}
                  </h3>
                  <div className="space-y-3">
                    {subjectTopics.map((topic) => {
                      const isSubmitting = submittingTopicId === topic.topic_id;
                      const scoreValue = scoreInputs[topic.topic_id] ?? '';

                      return (
                        <div
                          key={topic.topic_id}
                          className="flex flex-col sm:flex-row sm:items-center sm:justify-between bg-white p-3.5 rounded-lg border border-gray-200 gap-3 hover:border-gray-300 transition-colors"
                        >
                          <div className="flex-1">
                            <span className="font-medium text-gray-900 text-sm">
                              {topic.topic_name}
                            </span>
                            {typeof topic.mastery === 'number' && (
                              <span className="ml-2.5 text-xs text-gray-500">
                                Current Mastery:{' '}
                                <span className="font-medium text-gray-700">
                                  {Math.round(topic.mastery * 100)}%
                                </span>
                              </span>
                            )}
                          </div>

                          <div className="flex items-center gap-2">
                            <input
                              type="number"
                              min="0"
                              max="100"
                              step="any"
                              placeholder="0 - 100"
                              value={scoreValue}
                              onChange={(e) =>
                                handleScoreChange(topic.topic_id, e.target.value)
                              }
                              disabled={isSubmitting}
                              className="w-28 px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-100"
                            />
                            <button
                              type="button"
                              onClick={() => handleRecordScore(topic)}
                              disabled={isSubmitting}
                              className="inline-flex items-center justify-center px-3.5 py-1.5 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              {isSubmitting ? (
                                <>
                                  <svg
                                    className="animate-spin -ml-0.5 mr-2 h-4 w-4 text-white"
                                    xmlns="http://www.w3.org/2000/svg"
                                    fill="none"
                                    viewBox="0 0 24 24"
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
                                  <span>Saving...</span>
                                </>
                              ) : (
                                'Record Score'
                              )}
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Recent Performance Records ──────────────────────────────── */}
      {selectedStudentId && !loadingStudentData && !dataError && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 space-y-4">
          <div className="border-b border-gray-200 pb-3 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">
              Recent Performance Records
            </h2>
            <span className="text-xs text-gray-500">
              Total records: {records.length}
            </span>
          </div>

          {records.length === 0 ? (
            <div className="text-center py-8 text-sm text-gray-500">
              No performance records yet for this student.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead>
                  <tr className="bg-gray-50">
                    <th
                      scope="col"
                      className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
                    >
                      Topic Name
                    </th>
                    <th
                      scope="col"
                      className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
                    >
                      Score
                    </th>
                    <th
                      scope="col"
                      className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
                    >
                      Recorded At
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {records.map((record) => {
                    const topicName =
                      topicNameMap[record.topic_id] || record.topic_id;

                    return (
                      <tr key={record.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 whitespace-nowrap font-medium text-gray-900">
                          {topicName}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <ScoreBadge score={record.score} />
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-gray-500">
                          {formatDate(record.recorded_at)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
