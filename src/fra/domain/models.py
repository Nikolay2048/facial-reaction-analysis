from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class FrameData:
    frame_index: int
    timestamp_ms: float
    image: np.ndarray | None
    face_detected: bool
    landmarks: np.ndarray | None = None
    quality_score: float = 0.0
    quality_flags: list[str] = field(default_factory=list)


@dataclass
class FacialFeatureVector:
    frame_index: int
    timestamp_ms: float
    eye_openness: float
    eyebrow_raise: float
    mouth_openness: float
    lip_corner_movement: float
    facial_asymmetry: float
    response_intensity: float


@dataclass
class StimulusDescriptor:
    stimulus_id: str
    description: str
    category: str = "generic"
    source_dataset: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReactionProfile:
    stimulus_id: str
    timestamps_ms: list[float]
    features: list[dict[str, float]]
    onset_ms: float | None = None
    peak_ms: float | None = None
    recovery_ms: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class NormativeProfile:
    stimulus_category: str
    expected_features: list[dict[str, float]]
    timestamps_ms: list[float]
    thresholds: dict[str, float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DeviationResult:
    global_score: float
    amplitude_score: float
    latency_score: float
    symmetry_score: float
    recovery_score: float
    confidence: float
    warnings: list[str] = field(default_factory=list)


@dataclass
class AnalysisArtifacts:
    stimulus: StimulusDescriptor
    normative_profile: NormativeProfile
    reaction_profile: ReactionProfile
    deviation_result: DeviationResult
    frame_data: list[FrameData]
    feature_vectors: list[FacialFeatureVector]
    comparison: dict[str, float]
    interpretation: dict[str, Any] = field(default_factory=dict)
