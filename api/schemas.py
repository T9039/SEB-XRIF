"""Request and response schemas for the SEB-XRIF API.

The prediction request mirrors the 16 predictors of the xAPI Educational
Mining Dataset. Feature order is pinned in the model metadata; the API builds
the input vector from these named fields so column reordering cannot silently
corrupt predictions.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str


class PredictionRequest(BaseModel):
    gender: str
    NationalITy: str
    PlaceofBirth: str
    StageID: str
    GradeID: str
    SectionID: str
    Topic: str
    Semester: str
    Relation: str
    ParentAnsweringSurvey: str
    ParentschoolSatisfaction: str
    StudentAbsenceDays: str
    raisedhands: int = Field(ge=0)
    VisITedResources: int = Field(ge=0)
    AnnouncementsView: int = Field(ge=0)
    Discussion: int = Field(ge=0)


class PredictionResponse(BaseModel):
    prediction: str
    probabilities: dict[str, float]
    confidence: float
