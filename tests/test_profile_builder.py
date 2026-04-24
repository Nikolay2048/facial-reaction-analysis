from fra.domain.models import FacialFeatureVector
from fra.domain.models import NormativeProfile, ReactionProfile
from fra.profiling.alignment import TemporalAligner
from fra.profiling.reaction_profile_builder import ReactionProfileBuilder


def test_profile_builder_detects_peak() -> None:
    builder = ReactionProfileBuilder()
    vectors = [
        FacialFeatureVector(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01),
        FacialFeatureVector(1, 100.0, 0.1, 0.1, 0.1, 0.0, 0.0, 0.08),
        FacialFeatureVector(2, 200.0, 0.2, 0.2, 0.2, 0.0, 0.0, 0.15),
    ]
    profile = builder.build("stimulus", vectors)
    assert profile.peak_ms == 200.0


def test_temporal_aligner_resamples_actual_profile_to_normative_grid() -> None:
    aligner = TemporalAligner()
    actual = ReactionProfile(
        stimulus_id="stimulus",
        timestamps_ms=[0.0, 100.0, 200.0],
        features=[
            {"response_intensity": 0.0, "facial_asymmetry": 0.01},
            {"response_intensity": 0.5, "facial_asymmetry": 0.02},
            {"response_intensity": 1.0, "facial_asymmetry": 0.03},
        ],
    )
    normative = NormativeProfile(
        stimulus_category="generic",
        timestamps_ms=[0.0, 50.0, 100.0, 150.0, 200.0],
        expected_features=[
            {"response_intensity": 0.0, "facial_asymmetry": 0.01},
            {"response_intensity": 0.2, "facial_asymmetry": 0.01},
            {"response_intensity": 0.4, "facial_asymmetry": 0.02},
            {"response_intensity": 0.7, "facial_asymmetry": 0.02},
            {"response_intensity": 1.0, "facial_asymmetry": 0.03},
        ],
        thresholds={},
    )

    aligned_actual, aligned_normative = aligner.align(actual, normative)

    assert aligned_actual.timestamps_ms == normative.timestamps_ms
    assert aligned_normative.timestamps_ms == normative.timestamps_ms
    assert aligned_actual.features[1]["response_intensity"] == 0.25
    assert aligned_actual.features[3]["response_intensity"] == 0.75
    assert aligned_actual.peak_ms == 200.0
