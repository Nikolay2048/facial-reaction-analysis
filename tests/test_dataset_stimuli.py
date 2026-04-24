from __future__ import annotations

import json

from fra.api.dataset_analysis import DatasetStimulusAnalyzer
from fra.api.session import StimulusSessionRunner
from fra.domain.models import AnalysisArtifacts, DeviationResult, NormativeProfile, ReactionProfile, StimulusDescriptor
from fra.io.normative_profile_generator import DatasetNormativeProfileGenerator
from fra.io.stimulus_catalog import DatasetStimulusCatalog


def test_oasis_catalog_returns_existing_stimulus() -> None:
    catalog = DatasetStimulusCatalog()
    stimulus = catalog.get_descriptor(dataset="oasis", stimulus_id="I1")
    assert stimulus.stimulus_id == "I1"
    assert stimulus.source_dataset == "oasis"
    assert stimulus.metadata["image_path"]


def test_artemis_catalog_returns_existing_stimulus_with_expected_emotions() -> None:
    catalog = DatasetStimulusCatalog()
    stimulus = catalog.get_descriptor(
        dataset="artemis",
        stimulus_id="vincent-van-gogh_portrait-of-madame-ginoux-l-arlesienne-1890",
    )
    assert stimulus.source_dataset == "artemis"
    assert stimulus.metadata["image_path"]
    assert stimulus.metadata["expected_stimulus_emotions"]
    assert stimulus.metadata["expected_observed_emotions"]


def test_normative_profile_generator_builds_profile_from_dataset_metadata() -> None:
    generator = DatasetNormativeProfileGenerator()
    stimulus = StimulusDescriptor(
        stimulus_id="I1",
        description="Acorns 1",
        category="neutral",
        source_dataset="oasis",
        metadata={
            "valence_mean": 4.68,
            "arousal_mean": 2.34,
            "valence_sd": 0.95,
            "arousal_sd": 1.60,
        },
    )
    profile = generator.build(
        stimulus=stimulus,
        baseline_sec=1.0,
        stimulus_sec=3.0,
        recovery_sec=2.0,
    )
    assert profile.timestamps_ms[0] == 0.0
    assert profile.thresholds["latency_tolerance_ms"] > 0
    assert max(item["response_intensity"] for item in profile.expected_features) > 0.01


def test_normative_profile_generator_can_save_profile(tmp_path) -> None:
    generator = DatasetNormativeProfileGenerator()
    stimulus = StimulusDescriptor(
        stimulus_id="I1",
        description="Acorns 1",
        category="neutral",
        source_dataset="oasis",
        metadata={
            "valence_mean": 4.68,
            "arousal_mean": 2.34,
        },
    )
    profile = generator.build(
        stimulus=stimulus,
        baseline_sec=1.0,
        stimulus_sec=3.0,
        recovery_sec=2.0,
    )
    output_path = tmp_path / "generated_norm.json"
    generator.save(profile, str(output_path))

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["stimulus_category"] == "neutral"
    assert "expected_features" in payload


class StubCatalog:
    def get_descriptor(self, dataset: str, stimulus_id: str | None, category: str | None) -> StimulusDescriptor:
        return StimulusDescriptor(
            stimulus_id="I1",
            description="Acorns 1",
            category="neutral",
            source_dataset="oasis",
            metadata={
                "image_path": "image.jpg",
                "valence_mean": 4.68,
                "arousal_mean": 2.34,
                "valence_sd": 0.95,
                "arousal_sd": 1.60,
            },
        )

    def list_entries(self, dataset: str, category: str | None = None, limit: int | None = None):
        from fra.io.stimulus_catalog import StimulusCatalogEntry

        entries = [
            StimulusCatalogEntry(
                stimulus_id=f"I{index}",
                dataset=dataset,
                category="neutral",
                description=f"Stimulus {index}",
                image_path=f"image_{index}.jpg",
                valence_mean=4.68,
                arousal_mean=2.34,
            )
            for index in range(1, 5)
        ]
        return entries[:limit] if limit is not None else entries


class StubNormGenerator:
    def __init__(self) -> None:
        self.saved_path: str | None = None

    def build(self, stimulus: StimulusDescriptor, baseline_sec: float, stimulus_sec: float, recovery_sec: float) -> NormativeProfile:
        return NormativeProfile(
            stimulus_category=stimulus.category,
            expected_features=[{"response_intensity": 0.1, "facial_asymmetry": 0.01}],
            timestamps_ms=[0.0],
            thresholds={"latency_tolerance_ms": 250.0},
        )

    def save(self, normative_profile: NormativeProfile, output_path: str) -> str:
        self.saved_path = output_path
        return output_path


class StubRecorder:
    def record(
        self,
        stimulus_image_path: str,
        output_video_path: str,
        camera_index: int,
        baseline_sec: float,
        stimulus_sec: float,
        recovery_sec: float,
        headless: bool = False,
    ) -> str:
        return output_video_path


class StubPipeline:
    def run_with_profile(
        self,
        video_path: str,
        stimulus: StimulusDescriptor,
        normative_profile: NormativeProfile,
        output_json_path: str,
        output_csv_path: str | None = None,
        normative_profile_path: str | None = None,
    ) -> AnalysisArtifacts:
        return AnalysisArtifacts(
            stimulus=stimulus,
            normative_profile=normative_profile,
            reaction_profile=ReactionProfile(
                stimulus_id=stimulus.stimulus_id,
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
            frame_data=[],
            feature_vectors=[],
            comparison={"amplitude_gap": 0.0},
            interpretation={
                "expected_stimulus_emotions": ["contentment"],
                "expected_observed_emotions": ["neutral", "happy"],
                "actual_observed_emotion": "neutral",
                "alignment": "aligned",
                "summary": "summary",
            },
        )


def test_session_runner_uses_dataset_stimulus_and_generated_norm(tmp_path) -> None:
    runner = object.__new__(StimulusSessionRunner)
    runner.catalog = StubCatalog()
    runner.norm_generator = StubNormGenerator()
    runner.recorder = StubRecorder()
    runner.pipeline = StubPipeline()

    artifacts = runner.run(
        dataset="oasis",
        stimulus_id="I1",
        output_json_path=str(tmp_path / "report.json"),
        output_csv_path=str(tmp_path / "timeline.csv"),
        captured_video_path=str(tmp_path / "capture.mp4"),
        generated_norm_path=str(tmp_path / "norm.json"),
        headless=True,
    )

    assert artifacts.stimulus.source_dataset == "oasis"
    assert artifacts.normative_profile.stimulus_category == "neutral"
    assert runner.norm_generator.saved_path == str(tmp_path / "norm.json")


def test_catalog_list_entries_respects_limit() -> None:
    catalog = DatasetStimulusCatalog()
    entries = catalog.list_entries(dataset="oasis", limit=3)
    assert len(entries) == 3


def test_dataset_analyzer_uses_generated_norm_for_prerecorded_video(tmp_path) -> None:
    analyzer = object.__new__(DatasetStimulusAnalyzer)
    analyzer.catalog = StubCatalog()
    analyzer.norm_generator = StubNormGenerator()
    analyzer.pipeline = StubPipeline()

    artifacts = analyzer.analyze_video(
        video_path="reaction.mp4",
        dataset="oasis",
        stimulus_id="I1",
        output_json_path=str(tmp_path / "report.json"),
        output_csv_path=str(tmp_path / "timeline.csv"),
        generated_norm_path=str(tmp_path / "generated_norm.json"),
    )

    assert artifacts.stimulus.stimulus_id == "I1"
    assert artifacts.normative_profile.thresholds["latency_tolerance_ms"] == 250.0
    assert analyzer.norm_generator.saved_path == str(tmp_path / "generated_norm.json")


def test_session_runner_builds_final_study_report(tmp_path) -> None:
    runner = object.__new__(StimulusSessionRunner)
    runner.catalog = StubCatalog()
    runner.norm_generator = StubNormGenerator()
    runner.recorder = StubRecorder()
    runner.pipeline = StubPipeline()
    from fra.reports.session_report import SessionReportBuilder

    runner.session_report_builder = SessionReportBuilder()

    report = runner.run_study(
        dataset="oasis",
        count=2,
        output_json_path=str(tmp_path / "study.json"),
        output_csv_path=str(tmp_path / "study.csv"),
        artifacts_dir=str(tmp_path / "artifacts"),
        headless=True,
        seed=7,
    )

    payload = json.loads((tmp_path / "study.json").read_text(encoding="utf-8"))
    assert report["stimulus_count"] == 2
    assert payload["stimulus_count"] == 2
    assert "mean_global_score" in payload
    assert (tmp_path / "study.csv").exists()
