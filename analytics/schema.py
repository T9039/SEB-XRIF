"""Pandera schema for the xAPI Educational Mining Dataset (Kalboard 360).

Validates the 16 predictors and the three-class target before any modelling
happens. The dataset is published pre-cleaned, so this schema asserts that
property rather than assuming it.
"""
from __future__ import annotations

import pandera as pa
from pandera import Check, Column, DataFrameSchema

CATEGORICAL = [
    "gender",
    "NationalITy",
    "PlaceofBirth",
    "StageID",
    "GradeID",
    "SectionID",
    "Topic",
    "Semester",
    "Relation",
    "ParentAnsweringSurvey",
    "ParentschoolSatisfaction",
    "StudentAbsenceDays",
]

BEHAVIOURAL = [
    "raisedhands",
    "VisITedResources",
    "AnnouncementsView",
    "Discussion",
]

SCHEMA = DataFrameSchema(
    {
        **{name: Column(str) for name in CATEGORICAL},
        **{name: Column(int, Check.ge(0)) for name in BEHAVIOURAL},
        "Class": Column(str, Check.isin(["L", "M", "H"])),
    },
    strict=True,
    coerce=True,
)


def validate(df):
    """Validate and return a coerced copy of the learner dataset."""
    return SCHEMA.validate(df, lazy=True)
