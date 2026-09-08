-- ═══════════════════════════════════════════════════════════════
-- AI-Powered Student Workload Balancer — Database Schema
-- Run this in your Supabase SQL Editor (https://supabase.com/dashboard)
-- ═══════════════════════════════════════════════════════════════

-- ── 1. Students ──────────────────────────────────────────────
CREATE TABLE students (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE
);

-- ── 2. Subjects (shared curriculum, not per-student) ─────────
CREATE TABLE subjects (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    code        TEXT NOT NULL UNIQUE
);

-- ── 3. Enrollments (many-to-many: student ↔ subject) ────────
CREATE TABLE enrollments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject_id  UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    UNIQUE(student_id, subject_id)
);

-- ── 4. Topics (hangs off Subject, shared by all students) ────
CREATE TABLE topics (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id  UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    name        TEXT NOT NULL
);

-- ── 5. Assignments (deadline/urgency signal only) ────────────
CREATE TABLE assignments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id    UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    due_date    DATE NOT NULL,
    title       TEXT NOT NULL
);

-- ── 6. Performance Records (multiple per student+topic) ──────
CREATE TABLE performance_records (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    topic_id    UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    score       NUMERIC NOT NULL CHECK (score >= 0 AND score <= 100),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── 7. Study Plans (umbrella container per student) ──────────
CREATE TABLE study_plans (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    start_date  DATE NOT NULL,
    end_date    DATE NOT NULL
);

-- ── 8. Study Sessions (individual blocks within a plan) ──────
CREATE TABLE study_sessions (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id           UUID NOT NULL REFERENCES study_plans(id) ON DELETE CASCADE,
    topic_id          UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    date              DATE NOT NULL,
    duration_minutes  INTEGER NOT NULL CHECK (duration_minutes > 0),
    status            TEXT NOT NULL DEFAULT 'pending'
                      CHECK (status IN ('pending', 'done', 'missed'))
);
