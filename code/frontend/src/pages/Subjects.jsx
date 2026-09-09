import React, { useState, useEffect, useCallback } from 'react';
import {
  fetchSubjects,
  createSubject,
  deleteSubject,
  fetchTopicsBySubject,
  createTopic,
  deleteTopic,
} from '../api/client.js';

/**
 * Subjects & Topics Management Page.
 *
 * Allows users to:
 * 1. View all subjects and add new subjects (name + code).
 * 2. Delete subjects (with confirmation).
 * 3. Expand/collapse subject cards to view topics.
 * 4. Fetch topics per subject dynamically.
 * 5. Add new topics directly within each subject card (subject_id auto-filled).
 * 6. Delete individual topics.
 */
export default function Subjects() {
  // ── Subjects state ──────────────────────────────────────────
  const [subjects, setSubjects] = useState([]);
  const [loadingSubjects, setLoadingSubjects] = useState(true);
  const [subjectsError, setSubjectsError] = useState(null);

  // ── New Subject form state ──────────────────────────────────
  const [newSubjectName, setNewSubjectName] = useState('');
  const [newSubjectCode, setNewSubjectCode] = useState('');
  const [isCreatingSubject, setIsCreatingSubject] = useState(false);
  const [createSubjectError, setCreateSubjectError] = useState(null);

  // ── Per-subject expanded & topics state ─────────────────────
  // expandedSubjects: { [subjectId]: boolean }
  const [expandedSubjects, setExpandedSubjects] = useState({});
  // topicsBySubject: { [subjectId]: Topic[] }
  const [topicsBySubject, setTopicsBySubject] = useState({});
  // loadingTopics: { [subjectId]: boolean }
  const [loadingTopics, setLoadingTopics] = useState({});
  // topicsError: { [subjectId]: string | null }
  const [topicsError, setTopicsError] = useState({});

  // ── Per-subject Add Topic form state ────────────────────────
  // newTopicNames: { [subjectId]: string }
  const [newTopicNames, setNewTopicNames] = useState({});
  // isCreatingTopic: { [subjectId]: boolean }
  const [isCreatingTopic, setIsCreatingTopic] = useState({});
  // createTopicError: { [subjectId]: string | null }
  const [createTopicError, setCreateTopicError] = useState({});

  // ── Deletion loading states ─────────────────────────────────
  const [deletingSubjectId, setDeletingSubjectId] = useState(null);
  const [deletingTopicId, setDeletingTopicId] = useState(null);

  // ── Global alert message ────────────────────────────────────
  const [actionFeedback, setActionFeedback] = useState(null);

  /**
   * Helper to display temporary action feedback notifications.
   */
  const showFeedback = (message, type = 'success') => {
    setActionFeedback({ message, type });
    setTimeout(() => {
      setActionFeedback(null);
    }, 4000);
  };

  /**
   * Fetch all subjects from the API.
   */
  const loadSubjects = useCallback(async () => {
    setLoadingSubjects(true);
    setSubjectsError(null);
    try {
      const data = await fetchSubjects();
      setSubjects(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error fetching subjects:', err);
      setSubjectsError(err.message || 'Failed to fetch subjects. Please try again.');
    } finally {
      setLoadingSubjects(false);
    }
  }, []);

  // Initial load on mount
  useEffect(() => {
    loadSubjects();
  }, [loadSubjects]);

  /**
   * Fetch topics for a specific subject.
   */
  const loadTopics = useCallback(async (subjectId) => {
    setLoadingTopics((prev) => ({ ...prev, [subjectId]: true }));
    setTopicsError((prev) => ({ ...prev, [subjectId]: null }));
    try {
      const data = await fetchTopicsBySubject(subjectId);
      setTopicsBySubject((prev) => ({
        ...prev,
        [subjectId]: Array.isArray(data) ? data : [],
      }));
    } catch (err) {
      console.error(`Error fetching topics for subject ${subjectId}:`, err);
      setTopicsError((prev) => ({
        ...prev,
        [subjectId]: err.message || 'Failed to load topics for this subject.',
      }));
    } finally {
      setLoadingTopics((prev) => ({ ...prev, [subjectId]: false }));
    }
  }, []);

  /**
   * Toggle expansion of a subject card.
   * If expanding for the first time, automatically fetches the topics.
   */
  const handleToggleExpand = (subjectId) => {
    const isCurrentlyExpanded = !!expandedSubjects[subjectId];
    const willExpand = !isCurrentlyExpanded;

    setExpandedSubjects((prev) => ({
      ...prev,
      [subjectId]: willExpand,
    }));

    // Fetch topics if opening and not loaded yet
    if (willExpand && topicsBySubject[subjectId] === undefined) {
      loadTopics(subjectId);
    }
  };

  /**
   * Handle creating a new subject.
   */
  const handleCreateSubject = async (e) => {
    e.preventDefault();
    const trimmedName = newSubjectName.trim();
    const trimmedCode = newSubjectCode.trim().toUpperCase();

    if (!trimmedName || !trimmedCode) {
      setCreateSubjectError('Both subject name and code are required.');
      return;
    }

    setIsCreatingSubject(true);
    setCreateSubjectError(null);

    try {
      const created = await createSubject({
        name: trimmedName,
        code: trimmedCode,
      });

      // Add new subject to list and reset form
      setSubjects((prev) => [...prev, created]);
      setNewSubjectName('');
      setNewSubjectCode('');

      // Auto-expand newly created subject with empty topics
      setExpandedSubjects((prev) => ({ ...prev, [created.id]: true }));
      setTopicsBySubject((prev) => ({ ...prev, [created.id]: [] }));

      showFeedback(`Subject "${created.name}" (${created.code}) created successfully!`);
    } catch (err) {
      console.error('Error creating subject:', err);
      setCreateSubjectError(err.message || 'Failed to create subject. Please check inputs.');
    } finally {
      setIsCreatingSubject(false);
    }
  };

  /**
   * Handle deleting a subject.
   */
  const handleDeleteSubject = async (e, subject) => {
    e.stopPropagation(); // Avoid triggering card accordion toggle

    const confirmMsg = `Are you sure you want to delete "${subject.name}" (${subject.code})? All associated topics will also be permanently deleted.`;
    if (!window.confirm(confirmMsg)) {
      return;
    }

    setDeletingSubjectId(subject.id);
    try {
      await deleteSubject(subject.id);

      // Remove from subjects list
      setSubjects((prev) => prev.filter((s) => s.id !== subject.id));

      // Clean up cached topics & expansion state
      setTopicsBySubject((prev) => {
        const copy = { ...prev };
        delete copy[subject.id];
        return copy;
      });
      setExpandedSubjects((prev) => {
        const copy = { ...prev };
        delete copy[subject.id];
        return copy;
      });

      showFeedback(`Subject "${subject.name}" was deleted.`);
    } catch (err) {
      console.error('Error deleting subject:', err);
      alert(`Failed to delete subject: ${err.message || 'Unknown error'}`);
    } finally {
      setDeletingSubjectId(null);
    }
  };

  /**
   * Handle input change for a subject's new topic field.
   */
  const handleTopicInputChange = (subjectId, value) => {
    setNewTopicNames((prev) => ({ ...prev, [subjectId]: value }));
    if (createTopicError[subjectId]) {
      setCreateTopicError((prev) => ({ ...prev, [subjectId]: null }));
    }
  };

  /**
   * Handle adding a new topic to a subject.
   */
  const handleCreateTopic = async (e, subjectId) => {
    e.preventDefault();
    const topicName = (newTopicNames[subjectId] || '').trim();

    if (!topicName) {
      setCreateTopicError((prev) => ({
        ...prev,
        [subjectId]: 'Topic name cannot be empty.',
      }));
      return;
    }

    setIsCreatingTopic((prev) => ({ ...prev, [subjectId]: true }));
    setCreateTopicError((prev) => ({ ...prev, [subjectId]: null }));

    try {
      const created = await createTopic({
        subject_id: subjectId,
        name: topicName,
      });

      // Update topic list for this subject
      setTopicsBySubject((prev) => ({
        ...prev,
        [subjectId]: [...(prev[subjectId] || []), created],
      }));

      // Clear input
      setNewTopicNames((prev) => ({ ...prev, [subjectId]: '' }));
      showFeedback(`Topic "${created.name}" added successfully.`);
    } catch (err) {
      console.error('Error creating topic:', err);
      setCreateTopicError((prev) => ({
        ...prev,
        [subjectId]: err.message || 'Failed to add topic.',
      }));
    } finally {
      setIsCreatingTopic((prev) => ({ ...prev, [subjectId]: false }));
    }
  };

  /**
   * Handle deleting a topic.
   */
  const handleDeleteTopic = async (subjectId, topic) => {
    const confirmMsg = `Are you sure you want to delete the topic "${topic.name}"?`;
    if (!window.confirm(confirmMsg)) {
      return;
    }

    setDeletingTopicId(topic.id);
    try {
      await deleteTopic(topic.id);

      // Remove topic from local state
      setTopicsBySubject((prev) => ({
        ...prev,
        [subjectId]: (prev[subjectId] || []).filter((t) => t.id !== topic.id),
      }));

      showFeedback(`Topic "${topic.name}" was deleted.`);
    } catch (err) {
      console.error('Error deleting topic:', err);
      alert(`Failed to delete topic: ${err.message || 'Unknown error'}`);
    } finally {
      setDeletingTopicId(null);
    }
  };

  return (
    <div className="space-y-8">
      {/* ── Page Header ───────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-gray-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 tracking-tight">
            Subjects & Topics
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Create and organize subjects, manage course curricula, and define study topics.
          </p>
        </div>
        <button
          onClick={loadSubjects}
          disabled={loadingSubjects}
          className="inline-flex items-center gap-1.5 self-start sm:self-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1 disabled:opacity-50 transition-colors shadow-sm"
          title="Refresh subjects list"
        >
          <svg
            className={`w-4 h-4 text-gray-500 ${loadingSubjects ? 'animate-spin' : ''}`}
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
          <span>Refresh</span>
        </button>
      </div>

      {/* ── Toast Feedback Notification ───────────────────────── */}
      {actionFeedback && (
        <div
          className={`p-4 rounded-lg flex items-center justify-between transition-all ${
            actionFeedback.type === 'error'
              ? 'bg-red-50 text-red-800 border border-red-200'
              : 'bg-green-50 text-green-800 border border-green-200'
          }`}
        >
          <div className="flex items-center gap-2">
            {actionFeedback.type === 'error' ? (
              <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            )}
            <span className="text-sm font-medium">{actionFeedback.message}</span>
          </div>
          <button
            onClick={() => setActionFeedback(null)}
            className="text-gray-400 hover:text-gray-600 focus:outline-none"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* ── Add Subject Section ────────────────────────────────── */}
      <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 sm:p-6 transition-shadow hover:shadow-md">
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
            </svg>
          </div>
          <h2 className="text-lg font-bold text-gray-900">Add New Subject</h2>
        </div>

        {createSubjectError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg flex items-center gap-2">
            <svg className="w-4 h-4 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
            <span>{createSubjectError}</span>
          </div>
        )}

        <form onSubmit={handleCreateSubject} className="grid grid-cols-1 sm:grid-cols-12 gap-4 items-end">
          <div className="sm:col-span-6">
            <label htmlFor="subject-name" className="block text-xs font-semibold uppercase tracking-wider text-gray-700 mb-1">
              Subject Name <span className="text-red-500">*</span>
            </label>
            <input
              id="subject-name"
              type="text"
              required
              value={newSubjectName}
              onChange={(e) => setNewSubjectName(e.target.value)}
              placeholder="e.g. Data Structures & Algorithms"
              className="w-full px-3.5 py-2 text-sm bg-gray-50 border border-gray-300 rounded-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
              disabled={isCreatingSubject}
            />
          </div>

          <div className="sm:col-span-3">
            <label htmlFor="subject-code" className="block text-xs font-semibold uppercase tracking-wider text-gray-700 mb-1">
              Code <span className="text-red-500">*</span>
            </label>
            <input
              id="subject-code"
              type="text"
              required
              value={newSubjectCode}
              onChange={(e) => setNewSubjectCode(e.target.value)}
              placeholder="e.g. CS201"
              className="w-full px-3.5 py-2 text-sm bg-gray-50 border border-gray-300 rounded-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 uppercase transition-colors"
              disabled={isCreatingSubject}
            />
          </div>

          <div className="sm:col-span-3">
            <button
              type="submit"
              disabled={isCreatingSubject || !newSubjectName.trim() || !newSubjectCode.trim()}
              className="w-full inline-flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isCreatingSubject ? (
                <>
                  <svg className="animate-spin w-4 h-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  <span>Adding...</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span>Add Subject</span>
                </>
              )}
            </button>
          </div>
        </form>
      </section>

      {/* ── Subjects Listing ───────────────────────────────────── */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-gray-900">Enrolled Subjects</h2>
            <span className="px-2.5 py-0.5 text-xs font-semibold bg-gray-200 text-gray-700 rounded-full">
              {subjects.length}
            </span>
          </div>
          <span className="text-xs text-gray-500 italic">Click a subject card to view or add topics</span>
        </div>

        {/* Global Loading State for Subjects */}
        {loadingSubjects && (
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center shadow-sm">
            <div className="inline-flex items-center justify-center p-3 bg-indigo-50 text-indigo-600 rounded-full mb-3 animate-pulse">
              <svg className="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </div>
            <p className="text-gray-600 font-medium text-sm">Loading subjects from database...</p>
          </div>
        )}

        {/* Global Error State for Subjects */}
        {!loadingSubjects && subjectsError && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center shadow-sm">
            <svg className="w-10 h-10 text-red-500 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-sm font-bold text-red-800">Failed to load subjects</h3>
            <p className="mt-1 text-xs text-red-600 max-w-md mx-auto">{subjectsError}</p>
            <button
              onClick={loadSubjects}
              className="mt-4 px-4 py-1.5 text-xs font-semibold bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors shadow-sm"
            >
              Retry
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loadingSubjects && !subjectsError && subjects.length === 0 && (
          <div className="bg-white rounded-xl border-2 border-dashed border-gray-300 p-12 text-center">
            <div className="w-12 h-12 mx-auto mb-3 text-gray-400 bg-gray-100 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h3 className="text-base font-semibold text-gray-900">No subjects found</h3>
            <p className="mt-1 text-sm text-gray-500 max-w-sm mx-auto">
              Get started by creating your first subject using the form above. Once created, you can add topics to each subject.
            </p>
          </div>
        )}

        {/* Subjects List */}
        {!loadingSubjects && !subjectsError && subjects.length > 0 && (
          <div className="space-y-4">
            {subjects.map((subject) => {
              const isExpanded = !!expandedSubjects[subject.id];
              const topics = topicsBySubject[subject.id] || [];
              const isLoadingTopicsForThis = !!loadingTopics[subject.id];
              const topicFetchError = topicsError[subject.id];
              const isDeletingSubject = deletingSubjectId === subject.id;
              const topicInputVal = newTopicNames[subject.id] || '';
              const isAddingTopic = !!isCreatingTopic[subject.id];
              const topicAddError = createTopicError[subject.id];

              return (
                <div
                  key={subject.id}
                  className={`bg-white rounded-xl border transition-all duration-200 overflow-hidden ${
                    isExpanded
                      ? 'border-indigo-300 shadow-md ring-1 ring-indigo-100'
                      : 'border-gray-200 shadow-sm hover:border-gray-300 hover:shadow'
                  }`}
                >
                  {/* ── Subject Card Header (Expandable Trigger) ── */}
                  <div
                    onClick={() => handleToggleExpand(subject.id)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleToggleExpand(subject.id);
                      }
                    }}
                    className="w-full px-5 py-4 flex items-center justify-between gap-4 cursor-pointer select-none bg-white hover:bg-gray-50/75 transition-colors"
                  >
                    <div className="flex items-center gap-3.5 min-w-0">
                      {/* Subject Code Badge */}
                      <span className="flex-shrink-0 inline-flex items-center px-2.5 py-1 text-xs font-bold uppercase tracking-wider text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-md">
                        {subject.code}
                      </span>

                      {/* Subject Name */}
                      <span className="text-base sm:text-lg font-semibold text-gray-900 truncate">
                        {subject.name}
                      </span>

                      {/* Topic Count Indicator */}
                      {topicsBySubject[subject.id] !== undefined && (
                        <span className="hidden sm:inline-flex items-center px-2 py-0.5 text-xs font-medium text-gray-600 bg-gray-100 rounded-full">
                          {topics.length} {topics.length === 1 ? 'topic' : 'topics'}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
                      {/* Delete Subject Button */}
                      <button
                        type="button"
                        onClick={(e) => handleDeleteSubject(e, subject)}
                        disabled={isDeletingSubject}
                        title={`Delete ${subject.name}`}
                        className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50"
                      >
                        {isDeletingSubject ? (
                          <svg className="animate-spin w-4 h-4 text-red-500" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path
                              className="opacity-75"
                              fill="currentColor"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            />
                          </svg>
                        ) : (
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth="2"
                              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                            />
                          </svg>
                        )}
                      </button>

                      {/* Expand / Collapse Chevron */}
                      <div className="p-1 text-gray-400 hover:text-gray-600">
                        <svg
                          className={`w-5 h-5 transform transition-transform duration-200 ${
                            isExpanded ? 'rotate-180 text-indigo-600' : ''
                          }`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </div>
                  </div>

                  {/* ── Subject Card Body (Topics Section) ──────── */}
                  {isExpanded && (
                    <div className="border-t border-gray-100 bg-gray-50/50 px-5 py-5 sm:px-6 space-y-5">
                      {/* Topic Fetch Error State */}
                      {topicFetchError && (
                        <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between text-xs text-red-700">
                          <span>{topicFetchError}</span>
                          <button
                            onClick={() => loadTopics(subject.id)}
                            className="font-semibold underline hover:text-red-900 ml-2"
                          >
                            Retry
                          </button>
                        </div>
                      )}

                      {/* Loading Topics State */}
                      {isLoadingTopicsForThis && (
                        <div className="py-6 flex items-center justify-center gap-2 text-sm text-gray-500">
                          <svg className="animate-spin w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path
                              className="opacity-75"
                              fill="currentColor"
                              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                            />
                          </svg>
                          <span>Loading topics...</span>
                        </div>
                      )}

                      {/* Topics List */}
                      {!isLoadingTopicsForThis && (
                        <div>
                          <div className="flex items-center justify-between mb-2.5">
                            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500">
                              Topics ({topics.length})
                            </h4>
                            <button
                              onClick={() => loadTopics(subject.id)}
                              title="Reload topics"
                              className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                            >
                              Refresh
                            </button>
                          </div>

                          {topics.length === 0 ? (
                            <div className="p-4 bg-white rounded-lg border border-dashed border-gray-200 text-center">
                              <p className="text-xs text-gray-500">
                                No topics added yet for <span className="font-semibold text-gray-700">{subject.name}</span>.
                              </p>
                              <p className="text-xs text-gray-400 mt-0.5">
                                Add topics below to begin scheduling study sessions.
                              </p>
                            </div>
                          ) : (
                            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                              {topics.map((topic, index) => {
                                const isDeletingThisTopic = deletingTopicId === topic.id;
                                return (
                                  <li
                                    key={topic.id}
                                    className="flex items-center justify-between gap-2 px-3 py-2 bg-white rounded-lg border border-gray-200 shadow-xs hover:border-indigo-200 transition-colors"
                                  >
                                    <div className="flex items-center gap-2 min-w-0">
                                      <span className="w-5 h-5 flex-shrink-0 rounded-full bg-indigo-50 text-indigo-600 text-[10px] font-bold flex items-center justify-center">
                                        {index + 1}
                                      </span>
                                      <span className="text-sm font-medium text-gray-800 truncate" title={topic.name}>
                                        {topic.name}
                                      </span>
                                    </div>
                                    <button
                                      type="button"
                                      onClick={() => handleDeleteTopic(subject.id, topic)}
                                      disabled={isDeletingThisTopic}
                                      title={`Delete topic ${topic.name}`}
                                      className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors disabled:opacity-50 flex-shrink-0"
                                    >
                                      {isDeletingThisTopic ? (
                                        <svg className="animate-spin w-3.5 h-3.5 text-red-500" fill="none" viewBox="0 0 24 24">
                                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                          <path
                                            className="opacity-75"
                                            fill="currentColor"
                                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                          />
                                        </svg>
                                      ) : (
                                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                          <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth="2"
                                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                          />
                                        </svg>
                                      )}
                                    </button>
                                  </li>
                                );
                              })}
                            </ul>
                          )}
                        </div>
                      )}

                      {/* ── Add Topic Form (Auto-fills subject_id) ── */}
                      <div className="pt-3 border-t border-gray-200/80">
                        {topicAddError && (
                          <div className="mb-2 p-2 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg flex items-center gap-1.5">
                            <svg className="w-3.5 h-3.5 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                              <path
                                fillRule="evenodd"
                                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                                clipRule="evenodd"
                              />
                            </svg>
                            <span>{topicAddError}</span>
                          </div>
                        )}

                        <form
                          onSubmit={(e) => handleCreateTopic(e, subject.id)}
                          className="flex flex-col sm:flex-row gap-2 items-stretch"
                        >
                          <div className="relative flex-1">
                            <input
                              type="text"
                              value={topicInputVal}
                              onChange={(e) => handleTopicInputChange(subject.id, e.target.value)}
                              placeholder={`New topic for ${subject.code} (e.g. Recursion, Limits...)`}
                              disabled={isAddingTopic}
                              className="w-full px-3 py-1.5 text-sm bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                            />
                          </div>

                          <button
                            type="submit"
                            disabled={isAddingTopic || !topicInputVal.trim()}
                            className="inline-flex items-center justify-center gap-1.5 px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                          >
                            {isAddingTopic ? (
                              <>
                                <svg className="animate-spin w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24">
                                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                  <path
                                    className="opacity-75"
                                    fill="currentColor"
                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                  />
                                </svg>
                                <span>Adding...</span>
                              </>
                            ) : (
                              <>
                                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                                </svg>
                                <span>Add Topic</span>
                              </>
                            )}
                          </button>
                        </form>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
