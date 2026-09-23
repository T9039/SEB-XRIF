"""Application database: SQLAlchemy models and a small repository.

The framework's data layer stores validated learner records, the xAPI activity
events that describe their behaviour, model predictions, and longitudinal
evaluation measurements. SQLite is the default for development and tests;
docker-compose runs the same code against PostgreSQL.

Examples:
    uv run python -m analytics.db init          # create tables
    uv run python -m analytics.db counts        # row counts
"""

from __future__ import annotations

import argparse
import os
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

import pandas as pd
from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
    func,
    select,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

from .config import get_settings


class Base(DeclarativeBase):
    """Declarative base for all SEB-XRIF tables."""


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Learner(Base):
    """A learner and the 16 predictors used by the analytics layer."""

    __tablename__ = "learners"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    gender: Mapped[str] = mapped_column(String(16))
    nationality: Mapped[str] = mapped_column("NationalITy", String(64))
    place_of_birth: Mapped[str] = mapped_column("PlaceofBirth", String(64))
    stage_id: Mapped[str] = mapped_column("StageID", String(32))
    grade_id: Mapped[str] = mapped_column("GradeID", String(32))
    section_id: Mapped[str] = mapped_column("SectionID", String(16))
    topic: Mapped[str] = mapped_column("Topic", String(64))
    semester: Mapped[str] = mapped_column("Semester", String(16))
    relation: Mapped[str] = mapped_column("Relation", String(32))
    parent_answering_survey: Mapped[str] = mapped_column(
        "ParentAnsweringSurvey", String(16)
    )
    parent_school_satisfaction: Mapped[str] = mapped_column(
        "ParentschoolSatisfaction", String(16)
    )
    student_absence_days: Mapped[str] = mapped_column("StudentAbsenceDays", String(16))

    raisedhands: Mapped[int] = mapped_column(Integer)
    visited_resources: Mapped[int] = mapped_column("VisITedResources", Integer)
    announcements_view: Mapped[int] = mapped_column("AnnouncementsView", Integer)
    discussion: Mapped[int] = mapped_column(Integer)

    target_class: Mapped[str | None] = mapped_column("Class", String(4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    events: Mapped[list[ActivityEvent]] = relationship(back_populates="learner")
    predictions: Mapped[list[Prediction]] = relationship(back_populates="learner")
    evaluations: Mapped[list[Evaluation]] = relationship(back_populates="learner")


class ActivityEvent(Base):
    """A single xAPI statement (actor-verb-object, with optional result)."""

    __tablename__ = "activity_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    statement_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    learner_id: Mapped[int] = mapped_column(ForeignKey("learners.id"), index=True)

    verb: Mapped[str] = mapped_column(String(64), index=True)
    activity: Mapped[str] = mapped_column(String(128))
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    raw: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    learner: Mapped[Learner] = relationship(back_populates="events")


class Prediction(Base):
    """A model prediction for a learner."""

    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    learner_id: Mapped[int] = mapped_column(ForeignKey("learners.id"), index=True)

    model_version: Mapped[str] = mapped_column(String(128))
    predicted_class: Mapped[str] = mapped_column(String(4))
    probabilities: Mapped[dict[str, float]] = mapped_column(JSON, default=dict)
    confidence: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    learner: Mapped[Learner] = relationship(back_populates="predictions")


class Evaluation(Base):
    """A longitudinal measurement (T0/T1/T2) or usability score."""

    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(primary_key=True)
    learner_id: Mapped[int | None] = mapped_column(
        ForeignKey("learners.id"), nullable=True, index=True
    )

    time_point: Mapped[str] = mapped_column(String(4))  # T0, T1, T2
    measure: Mapped[str] = mapped_column(String(32))  # e.g. score, sus
    value: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    learner: Mapped[Learner | None] = relationship(back_populates="evaluations")


# --------------------------------------------------------------------- engine
def get_engine(url: str | None = None) -> Engine:
    """Create an engine for the given URL, or the configured default."""
    resolved = url or os.environ.get("DATABASE_URL") or get_settings().database_url
    connect_args: dict[str, Any] = {}
    if resolved.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(resolved, future=True, connect_args=connect_args)


def init_db(engine: Engine) -> None:
    """Create all tables (development convenience; Alembic owns production)."""
    Base.metadata.create_all(engine)


@contextmanager
def session_scope(engine: Engine) -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# --------------------------------------------------------------- repository
LEARNER_FIELDS = (
    "external_id",
    "gender",
    "nationality",
    "place_of_birth",
    "stage_id",
    "grade_id",
    "section_id",
    "topic",
    "semester",
    "relation",
    "parent_answering_survey",
    "parent_school_satisfaction",
    "student_absence_days",
    "raisedhands",
    "visited_resources",
    "announcements_view",
    "discussion",
    "target_class",
)

#: Feature-frame column -> application database attribute. Used to move data
#: between the xAPI/CSV layer and Postgres in both directions.
FRAME_TO_DB = {
    "gender": "gender",
    "NationalITy": "nationality",
    "PlaceofBirth": "place_of_birth",
    "StageID": "stage_id",
    "GradeID": "grade_id",
    "SectionID": "section_id",
    "Topic": "topic",
    "Semester": "semester",
    "Relation": "relation",
    "ParentAnsweringSurvey": "parent_answering_survey",
    "ParentschoolSatisfaction": "parent_school_satisfaction",
    "StudentAbsenceDays": "student_absence_days",
    "raisedhands": "raisedhands",
    "VisITedResources": "visited_resources",
    "AnnouncementsView": "announcements_view",
    "Discussion": "discussion",
    "Class": "target_class",
}


def learners_frame(engine: Engine) -> pd.DataFrame:
    """Return the learners table as a feature frame (CSV column names)."""
    with session_scope(engine) as session:
        learners = session.scalars(select(Learner)).all()
    records: list[dict[str, Any]] = []
    for learner in learners:
        record: dict[str, Any] = {"external_id": learner.external_id}
        for frame_column, attribute in FRAME_TO_DB.items():
            record[frame_column] = getattr(learner, attribute)
        records.append(record)
    return pd.DataFrame(records, columns=list(FRAME_TO_DB))


def evaluations_frame(engine: Engine) -> pd.DataFrame:
    """Return the evaluations table as a tidy frame."""
    with session_scope(engine) as session:
        evaluations = session.scalars(select(Evaluation)).all()
    return pd.DataFrame(
        [
            {
                "learner_id": item.learner_id,
                "time_point": item.time_point,
                "measure": item.measure,
                "value": item.value,
            }
            for item in evaluations
        ],
        columns=["learner_id", "time_point", "measure", "value"],
    )


def upsert_learner(session: Session, data: dict[str, Any]) -> Learner:
    """Insert or update a learner keyed by ``external_id``."""
    learner = session.scalar(
        select(Learner).where(Learner.external_id == data["external_id"])
    )
    if learner is None:
        learner = Learner(**{k: data.get(k) for k in LEARNER_FIELDS})
        session.add(learner)
        session.flush()
        return learner
    for key in LEARNER_FIELDS:
        if key in data:
            setattr(learner, key, data[key])
    session.flush()
    return learner


def record_event(
    session: Session, learner: Learner, statement: dict[str, Any]
) -> ActivityEvent:
    """Persist an xAPI statement as an activity event."""
    event = ActivityEvent(
        statement_id=statement["id"],
        learner=learner,
        verb=statement["verb"],
        activity=statement["object"],
        score=statement.get("result", {}).get("score"),
        raw=statement,
    )
    session.add(event)
    session.flush()
    return event


def record_prediction(
    session: Session,
    learner: Learner,
    model_version: str,
    predicted_class: str,
    probabilities: dict[str, float],
    confidence: float,
) -> Prediction:
    """Persist a model prediction for a learner."""
    prediction = Prediction(
        learner=learner,
        model_version=model_version,
        predicted_class=predicted_class,
        probabilities=probabilities,
        confidence=confidence,
    )
    session.add(prediction)
    session.flush()
    return prediction


def record_evaluation(
    session: Session,
    time_point: str,
    measure: str,
    value: float,
    learner: Learner | None = None,
) -> Evaluation:
    """Persist a longitudinal or usability measurement."""
    evaluation = Evaluation(
        learner=learner, time_point=time_point, measure=measure, value=value
    )
    session.add(evaluation)
    session.flush()
    return evaluation


def counts(engine: Engine) -> dict[str, int]:
    """Return row counts for each table."""
    tables: Sequence[tuple[str, type[Base]]] = [
        ("learners", Learner),
        ("activity_events", ActivityEvent),
        ("predictions", Prediction),
        ("evaluations", Evaluation),
    ]
    with session_scope(engine) as session:
        return {
            name: int(session.scalar(select(func.count()).select_from(model)) or 0)
            for name, model in tables
        }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="SEB-XRIF database utilities.")
    parser.add_argument("command", choices=["init", "counts"])
    parser.add_argument("--url", default=None, help="Database URL override.")
    args = parser.parse_args(argv)

    engine = get_engine(args.url)
    if args.command == "init":
        init_db(engine)
        print(f"Initialised schema at {engine.url}")
    else:
        for name, value in counts(engine).items():
            print(f"{name}: {value}")


if __name__ == "__main__":
    main()
