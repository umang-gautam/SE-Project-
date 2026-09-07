# Backend setup

Everything runs from `code/`. You need a Supabase project with the eight
tables; ask the team for the URL and service key.

## Configure

```sh
cd code
cp .env.example .env
# edit .env: SUPABASE_URL, SUPABASE_SERVICE_KEY
```

`.env` is git-ignored and Docker-ignored. Keep it that way.

## Run with Docker (recommended)

```sh
docker compose up --build
```

- API: <http://localhost:8000>, interactive docs at <http://localhost:8000/docs>
- Postgres: `localhost:5432`, user/password/db all `balancer`

Create the tables in the local Postgres once:

```sh
docker compose run --rm api python scripts/init_db.py
```

Check everything is wired:

```sh
curl localhost:8000/health
# {"status":"ok","database":"ok","supabase":"ok"}
```

## Run without Docker

Python 3.10 or newer.

```sh
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

To also use the compose Postgres from a bare uvicorn, start only the database
with `docker compose up db` and uncomment `DATABASE_URL` in `.env`.

## Tests

From the repository root:

```sh
pytest
```

No credentials or network needed. The repository layer is monkeypatched.

## Adding an entity

Copy the four-file pattern from `students`: a schema in `app/schemas/`, a
repository in `app/repositories/`, a service in `app/services/`, a route in
`app/api/routes/`. Register the router in `app/main.py`. Add a model in
`app/models/` and import it in `app/models/__init__.py`.
