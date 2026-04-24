from fra.domain.models import DeviationResult, NormativeProfile, ReactionProfile, StimulusDescriptor
from fra.reports.csv_report import CSVReportBuilder
from fra.reports.json_report import JSONReportBuilder


def test_csv_report_builder() -> None:
    builder = CSVReportBuilder()
    profile = ReactionProfile(
        stimulus_id="x",
        timestamps_ms=[0.0],
        features=[{"response_intensity": 0.1}],
    )
    frame = builder.build(profile)
    assert "timestamp_ms" in frame.columns


def test_json_report_builder_includes_stimulus_and_normative_reference() -> None:
    builder = JSONReportBuilder()
    report = builder.build(
        stimulus=StimulusDescriptor(
            stimulus_id="pleasant_surprise",
            description="pleasant surprise image",
            category="positive",
            source_dataset="artemis",
        ),
        normative_profile=NormativeProfile(
            stimulus_category="positive",
            expected_features=[{"response_intensity": 0.2, "facial_asymmetry": 0.02}],
            timestamps_ms=[0.0],
            thresholds={"latency_tolerance_ms": 250.0},
        ),
        reaction_profile=ReactionProfile(
            stimulus_id="pleasant_surprise",
            timestamps_ms=[0.0],
            features=[{"response_intensity": 0.1, "facial_asymmetry": 0.01}],
        ),
        deviation_result=DeviationResult(
            global_score=0.1,
            amplitude_score=0.1,
            latency_score=0.1,
            symmetry_score=0.1,
            recovery_score=0.1,
            confidence=0.9,
        ),
        interpretation={
            "stimulus_source_dataset": "artemis",
            "stimulus_category": "positive",
            "expected_stimulus_emotions": ["awe", "amusement"],
            "expected_observed_emotions": ["surprise", "happy"],
            "reference_utterances": ["bright colors make a unique scene"],
            "actual_observed_emotion": "surprise",
            "peak_response_features": {"response_intensity": 0.1},
            "alignment": "aligned",
            "summary": "Expected visible reaction classes: surprise, happy.",
        },
        frame_data=[],
        video_path="sample.mp4",
    )
    assert report["stimulus"]["category"] == "positive"
    assert report["normative_reference"]["stimulus_category"] == "positive"
    assert report["interpretation"]["actual_observed_emotion"] == "surprise"
