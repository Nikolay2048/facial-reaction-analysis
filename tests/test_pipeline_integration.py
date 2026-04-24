from __future__ import annotations

import json

from fra.api.pipeline import ReactionAnalysisPipeline
from fra.domain.models import DeviationResult, FacialFeatureVector, FrameData, NormativeProfile, ReactionProfile, StimulusDescriptor


class StubVideoReader:
    def read(self, video_path: str) -> list[FrameData]:
        return [
            FrameData(frame_index=0, timestamp_ms=0.0, image=None, face_detected=True, landmarks=None, quality_score=0.9),
            FrameData(frame_index=1, timestamp_ms=200.0, image=None, face_detected=True, landmarks=None, quality_score=0.9),
            FrameData(frame_index=2, timestamp_ms=400.0, image=None, face_detected=True, landmarks=None, quality_score=0.9),
        ]


class PassthroughTracker:
    def process(self, frame_data: FrameData) -> FrameData:
        return frame_data


class PassthroughQualityAssessor:
    def assess(self, frame_data: FrameData) -> FrameData:
        frame_data.face_detected = True
        frame_data.quality_score = 0.9
        return frame_data


class StubGeometricExtractor:
    def __init__(self) -> None:
        self._index = 0
        self._vectors = [
            FacialFeatureVector(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01, 0.01),
            FacialFeatureVector(1, 200.0, 0.1, 0.1, 0.1, 0.0, 0.02, 0.20),
            FacialFeatureVector(2, 400.0, 0.2, 0.2, 0.2, 0.0, 0.05, 0.30),
        ]

    def extract(self, frame_data: FrameData) -> FacialFeatureVector:
        vector = self._vectors[self._index]
        self._index += 1
        return vector


class PassthroughTemporalExtractor:
    def enrich(self, feature_vectors: list[FacialFeatureVector]) -> list[FacialFeatureVector]:
        return feature_vectors


class PassthroughNormalizer:
    def normalize(self, feature_vectors: list[FacialFeatureVector]) -> list[FacialFeatureVector]:
        return feature_vectors


class StubProfileBuilder:
    def build(self, stimulus_id: str, feature_vectors: list[FacialFeatureVector]) -> ReactionProfile:
        return ReactionProfile(
            stimulus_id=stimulus_id,
            timestamps_ms=[0.0, 200.0, 400.0],
            features=[
                {"response_intensity": 0.01, "facial_asymmetry": 0.01},
                {"response_intensity": 0.20, "facial_asymmetry": 0.02},
                {"response_intensity": 0.30, "facial_asymmetry": 0.05},
            ],
            onset_ms=200.0,
            peak_ms=400.0,
            recovery_ms=400.0,
        )


class StubNormativeLoader:
    def load(self, normative_profile_path: str) -> NormativeProfile:
        return NormativeProfile(
            stimulus_category="positive",
            timestamps_ms=[0.0, 200.0, 400.0],
            expected_features=[
                {"response_intensity": 0.01, "facial_asymmetry": 0.01},
                {"response_intensity": 0.15, "facial_asymmetry": 0.02},
                {"response_intensity": 0.25, "facial_asymmetry": 0.03},
            ],
            thresholds={
                "amplitude_tolerance": 0.20,
                "latency_tolerance_ms": 250.0,
                "symmetry_tolerance": 0.10,
                "recovery_tolerance": 0.20,
            },
        )


class PassthroughAligner:
    def align(
        self,
        actual_profile: ReactionProfile,
        normative_profile: NormativeProfile,
    ) -> tuple[ReactionProfile, NormativeProfile]:
        return actual_profile, normative_profile


class StubConfidenceEstimator:
    def estimate(
        self,
        frame_data: list[FrameData],
        feature_vectors: list[FacialFeatureVector],
    ) -> float:
        return 0.95


class StubStimulusLoader:
    def load(self, description: str) -> StimulusDescriptor:
        return StimulusDescriptor(
            stimulus_id="pleasant_surprise_image",
            description=description,
            category="positive",
        )


def test_pipeline_generates_report_with_all_metrics(tmp_path) -> None:
    pipeline = object.__new__(ReactionAnalysisPipeline)
    pipeline.video_reader = StubVideoReader()
    pipeline.tracker = PassthroughTracker()
    pipeline.quality_assessor = PassthroughQualityAssessor()
    pipeline.geometric_extractor = StubGeometricExtractor()
    pipeline.temporal_extractor = PassthroughTemporalExtractor()
    pipeline.normalizer = PassthroughNormalizer()
    pipeline.profile_builder = StubProfileBuilder()
    pipeline.normative_loader = StubNormativeLoader()
    pipeline.aligner = PassthroughAligner()
    from fra.scoring.comparators import ProfileComparator
    from fra.scoring.deviation_calculator import DeviationCalculator
    from fra.scoring.reaction_interpreter import ReactionInterpreter
    from fra.io.report_writer import ReportWriter

    pipeline.comparator = ProfileComparator()
    pipeline.deviation_calculator = DeviationCalculator()
    pipeline.confidence_estimator = StubConfidenceEstimator()
    pipeline.reaction_interpreter = ReactionInterpreter()
    pipeline.report_writer = ReportWriter()
    pipeline.stimulus_loader = StubStimulusLoader()

    json_path = tmp_path / "report.json"
    csv_path = tmp_path / "timeline.csv"
    artifacts = pipeline.run(
        video_path="sample.mp4",
        stimulus_description="pleasant surprise image",
        normative_profile_path="norm.json",
        output_json_path=str(json_path),
        output_csv_path=str(csv_path),
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert artifacts.deviation_result.global_score >= 0.0
    assert "amplitude_score" in payload["deviation"]
    assert "latency_score" in payload["deviation"]
    assert "symmetry_score" in payload["deviation"]
    assert "recovery_score" in payload["deviation"]
    assert "confidence" in payload["deviation"]
    assert "interpretation" in payload
    assert csv_path.exists()
