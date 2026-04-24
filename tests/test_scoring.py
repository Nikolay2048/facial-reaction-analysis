import pytest

from fra.domain.models import NormativeProfile, ReactionProfile
from fra.scoring.comparators import ProfileComparator
from fra.scoring.deviation_calculator import DeviationCalculator


def test_deviation_score_range() -> None:
    calculator = DeviationCalculator()
    result = calculator.calculate(
        {
            "amplitude_gap": 0.2,
            "latency_gap_ms": 300.0,
            "symmetry_gap": 0.1,
            "recovery_gap": 0.2,
        },
        thresholds={
            "amplitude_tolerance": 0.4,
            "latency_tolerance_ms": 600.0,
            "symmetry_tolerance": 0.2,
            "recovery_tolerance": 0.4,
        },
    )
    assert 0.0 <= result.global_score <= 1.0


def test_deviation_calculator_uses_normative_thresholds_for_component_scores() -> None:
    calculator = DeviationCalculator()
    result = calculator.calculate(
        {
            "amplitude_gap": 0.3,
            "latency_gap_ms": 500.0,
            "symmetry_gap": 0.05,
            "recovery_gap": 0.1,
        },
        thresholds={
            "amplitude_tolerance": 0.3,
            "latency_tolerance_ms": 250.0,
            "symmetry_tolerance": 0.1,
            "recovery_tolerance": 0.2,
        },
    )

    assert result.amplitude_score == 1.0
    assert result.latency_score == 1.0
    assert result.symmetry_score == 0.5
    assert result.recovery_score == 0.5
    assert "Latency deviation exceeds the normative tolerance." in result.warnings


def test_profile_comparator_calculates_all_gap_metrics_against_normative_profile() -> None:
    comparator = ProfileComparator()
    actual_profile = ReactionProfile(
        stimulus_id="stimulus",
        timestamps_ms=[0.0, 200.0, 400.0, 600.0],
        features=[
            {"response_intensity": 0.01, "facial_asymmetry": 0.01},
            {"response_intensity": 0.20, "facial_asymmetry": 0.02},
            {"response_intensity": 0.30, "facial_asymmetry": 0.05},
            {"response_intensity": 0.04, "facial_asymmetry": 0.03},
        ],
        peak_ms=400.0,
        recovery_ms=600.0,
    )
    normative_profile = NormativeProfile(
        stimulus_category="generic",
        timestamps_ms=[0.0, 200.0, 400.0, 600.0],
        expected_features=[
            {"response_intensity": 0.01, "facial_asymmetry": 0.01},
            {"response_intensity": 0.10, "facial_asymmetry": 0.02},
            {"response_intensity": 0.25, "facial_asymmetry": 0.03},
            {"response_intensity": 0.02, "facial_asymmetry": 0.02},
        ],
        thresholds={},
    )

    comparison = comparator.compare(actual_profile, normative_profile)

    assert comparison["amplitude_gap"] == pytest.approx(0.05)
    assert comparison["latency_gap_ms"] == pytest.approx(0.0)
    assert comparison["symmetry_gap"] == pytest.approx(0.02)
    assert comparison["recovery_gap"] == pytest.approx(0.0)
