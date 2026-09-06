from sqlalchemy import create_engine, inspect

from app.models import Base

EXPECTED = {
    "students", "subjects", "enrollments", "topics",
    "assignments", "performance_records", "study_plans", "study_sessions",
}


def test_all_eight_tables_build():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    assert set(inspect(engine).get_table_names()) == EXPECTED
