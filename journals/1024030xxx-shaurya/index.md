# Shaurya's Journal

Roll No. 1024030xxx

Name: Shaurya

Backend track. Picks up from Khushi's Phase 4 (schema designed, models pending).

---

## 2026-09-01 — Phase 5: Dependency and encoding cleanup

**Status:** Complete

### What I did
- Re-saved `code/requirements.txt` as UTF-8 with LF line endings. It had been written as UTF-16 with CRLF from Windows, which pip cannot parse on Linux or in a Docker build.
- Added the two packages the code already imports but never declared: `httpx` (used by every repository to call Supabase) and `email-validator` (required by pydantic's `EmailStr`).
- Stripped the UTF-8 byte-order mark from 29 Python files under `code/app/`. Harmless to Python, noisy in diffs and breaks some linters.
- Added `code/.env.example` documenting the three environment variables the app reads.

### Key decisions & reasoning
- **Decision:** Pin `httpx` and `email-validator` to exact versions like the rest of the file.
  **Why:** The file is a lockfile in spirit. Mixing pinned and floating versions makes Docker builds non-reproducible.
- **Decision:** Ship `.env.example` instead of documenting variables only in prose.
  **Why:** A new teammate copies one file and fills in blanks. Also makes it obvious that `.env` itself must stay untracked.

### Challenges & how I solved them
- `pip install -r requirements.txt` failed with an encoding error before anything else could be tested. Confirmed with `file requirements.txt` that it was UTF-16, converted with Python.

### Next steps
- Make the API start without `DATABASE_URL`, since Supabase REST is the real data path.
- Turn `/health` into something a container orchestrator can actually use.
