"""Create all eight tables in the database named by DATABASE_URL.

Usage (from code/): PYTHONPATH=. python scripts/init_db.py
       or: docker compose run --rm api python scripts/init_db.py
Idempotent: existing tables are left alone.
"""
from app.core.database import get_engine
from app.models import Base

if __name__ == "__main__":
    engine = get_engine()
    Base.metadata.create_all(engine)
    print(f"schema ready on {engine.url.render_as_string(hide_password=True)}")
