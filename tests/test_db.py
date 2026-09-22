"""Feature and end-to-end tests for the database layer."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from analytics.db import (
    counts,
    get_engine,
    init_db,
    record_evaluation,
    record_event,
    record_prediction,
    session_scope,
    upsert_learner,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

LEARNER = {
    "external_id": "L001",
    "gender": "M",
    "nationality": "KW",
    "place_of_birth": "KuwaIT",
    "stage_id": "lowerlevel",
    "grade_id": "G-04",
    "section_id": "A",
    "topic": "IT",
    "semester": "F",
    "relation": "Father",
    "parent_answering_survey": "Yes",
    "parent_school_satisfaction": "Good",
    "student_absence_days": "Under-7",
    "raisedhands": 15,
    "visited_resources": 16,
    "announcements_view": 2,
    "discussion": 20,
    "target_class": "M",
}


# --------------------------------------------------------------------- feature
def test_init_and_repository_roundtrip():
    engine = get_engine("sqlite://")
    init_db(engine)

    with session_scope(engine) as session:
        learner = upsert_learner(session, LEARNER)
        record_event(
            session,
            learner,
            {
                "id": "stmt-1",
                "verb": "attempted",
                "object": "vr-defibrillator",
                "result": {"score": 0.82},
            },
        )
        record_prediction(
            session,
            learner,
            model_version="rf-test",
            predicted_class="M",
            probabilities={"L": 0.1, "M": 0.7, "H": 0.2},
            confidence=0.7,
        )
        record_evaluation(session, "T0", "score", 45.0, learner)

    assert counts(engine) == {
        "learners": 1,
        "activity_events": 1,
        "predictions": 1,
        "evaluations": 1,
    }


def test_upsert_is_idempotent():
    engine = get_engine("sqlite://")
    init_db(engine)

    with session_scope(engine) as session:
        upsert_learner(session, LEARNER)
    with session_scope(engine) as session:
        updated = dict(LEARNER, raisedhands=99, target_class="H")
        upsert_learner(session, updated)

    assert counts(engine)["learners"] == 1
    with session_scope(engine) as session:
        from sqlalchemy import select

        from analytics.db import Learner

        learner = session.scalar(select(Learner))
        assert learner is not None
        assert learner.raisedhands == 99
        assert learner.target_class == "H"


# ------------------------------------------------------------------------- e2e
def test_alembic_upgrade_creates_schema(tmp_path: Path):
    db_path = tmp_path / "seb.db"
    url = f"sqlite:///{db_path}"
    alembic = Path(sys.executable).parent / "alembic"

    completed = subprocess.run(
        [str(alembic), "upgrade", "head"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={"DATABASE_URL": url, "PATH": str(Path(sys.executable).parent)},
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert db_path.exists()

    engine = get_engine(url)
    assert set(counts(engine)) == {
        "learners",
        "activity_events",
        "predictions",
        "evaluations",
    }

    with session_scope(engine) as session:
        upsert_learner(session, LEARNER)
    assert counts(engine)["learners"] == 1
