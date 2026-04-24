from __future__ import annotations

from fra.api.pipeline import ReactionAnalysisPipeline
from fra.domain.models import AnalysisArtifacts
from fra.io.normative_profile_generator import DatasetNormativeProfileGenerator
from fra.io.stimulus_catalog import DatasetStimulusCatalog


class DatasetStimulusAnalyzer:
    def __init__(self) -> None:
        self.catalog = DatasetStimulusCatalog()
        self.norm_generator = DatasetNormativeProfileGenerator()
        self.pipeline = ReactionAnalysisPipeline()

    def analyze_video(
        self,
        video_path: str,
        dataset: str,
        output_json_path: str,
        output_csv_path: str | None = None,
        stimulus_id: str | None = None,
        category: str | None = None,
        baseline_sec: float = 1.0,
        stimulus_sec: float = 3.0,
        recovery_sec: float = 2.0,
        generated_norm_path: str | None = None,
    ) -> AnalysisArtifacts:
        stimulus = self.catalog.get_descriptor(
            dataset=dataset,
            stimulus_id=stimulus_id,
            category=category,
        )
        normative_profile = self.norm_generator.build(
            stimulus=stimulus,
            baseline_sec=baseline_sec,
            stimulus_sec=stimulus_sec,
            recovery_sec=recovery_sec,
        )
        if generated_norm_path:
            self.norm_generator.save(normative_profile, generated_norm_path)
        return self.pipeline.run_with_profile(
            video_path=video_path,
            stimulus=stimulus,
            normative_profile=normative_profile,
            output_json_path=output_json_path,
            output_csv_path=output_csv_path,
        )
