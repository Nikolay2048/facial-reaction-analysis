from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StimulusSchema(BaseModel):
    stimulus_id: str = Field(default="unknown")
    description: str
    category: str = Field(default="generic")
    source_dataset: str | None = None


class NormativeProfileSchema(BaseModel):
    stimulus_category: str
    timestamps_ms: list[float]
    expected_features: list[dict[str, float]]
    thresholds: dict[str, float]
    metadata: dict[str, Any] = Field(default_factory=dict)


class QualityReportSchema(BaseModel):
    processed_frames: int
    valid_frames: int
    tracking_success_rate: float


class ReactionProfileSchema(BaseModel):
    onset_ms: float | None = None
    peak_ms: float | None = None
    recovery_ms: float | None = None
    timestamps_ms: list[float]
    features: list[dict[str, float]]
    metadata: dict[str, Any] = Field(default_factory=dict)


class DeviationSchema(BaseModel):
    global_score: float
    amplitude_score: float
    latency_score: float
    symmetry_score: float
    recovery_score: float
    confidence: float


class NormativeReferenceSchema(BaseModel):
    stimulus_category: str
    thresholds: dict[str, float]
    metadata: dict[str, Any] = Field(default_factory=dict)


class InterpretationSchema(BaseModel):
    stimulus_source_dataset: str | None = None
    stimulus_category: str
    expected_stimulus_emotions: list[str] = Field(default_factory=list)
    expected_observed_emotions: list[str] = Field(default_factory=list)
    reference_utterances: list[str] = Field(default_factory=list)
    actual_observed_emotion: str
    peak_response_features: dict[str, float] = Field(default_factory=dict)
    alignment: str
    summary: str


class ReportSchema(BaseModel):
    input: dict[str, str]
    stimulus: StimulusSchema
    quality: QualityReportSchema
    normative_reference: NormativeReferenceSchema
    reaction_profile: ReactionProfileSchema
    deviation: DeviationSchema
    interpretation: InterpretationSchema
    warnings: list[str] = Field(default_factory=list)
    disclaimer: str = Field(
        default="This result is an analytical computer-vision metric and not a medical diagnosis."
    )
