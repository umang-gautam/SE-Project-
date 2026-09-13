# Setup

Everything lives under `code/`. You need a Supabase project with the tables
from `code/backend/schema.sql`: paste the file into the Supabase SQL editor once.

## Configure

```sh
cd code/backend
cp .env.example .env
# edit .env: SUPABASE_URL, SUPABASE_KEY
```

`.env` is git-ignored and docker-ignored. Keep it that way.

## Run everything with Docker

```sh
cd code
docker compose up --build
```

- App: <http://localhost:8080>
- API through the frontend proxy: <http://localhost:8080/api/health>

## Run the pieces directly

Backend, Python 3.10+:

```sh
cd code/backend
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload                        # http://localhost:8000/docs
```

Frontend, Node 22:

```sh
cd code/frontend
npm install
npm run dev                                          # http://localhost:5173, proxies /api to :8000
```

## Tests

From the repository root:

```sh
pytest
```

No credentials or network needed. Route tests patch services, agent tests patch
the agent's tools, and the scoring and allocation tests are pure functions.

## Adding an entity

Follow `students` through the layers: schema in `app/schemas/`, repository in
`app/repositories/`, service in `app/services/`, router in `app/api/routes/`,
then `include_router` in `app/main.py`. Add the table to `schema.sql` and the
client functions to `frontend/src/api/client.js`.
