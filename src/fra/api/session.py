from __future__ import annotations

import json
import random
from pathlib import Path

from fra.api.pipeline import ReactionAnalysisPipeline
from fra.domain.models import AnalysisArtifacts
from fra.io.normative_profile_generator import DatasetNormativeProfileGenerator
from fra.io.reaction_capture import StimulusReactionRecorder
from fra.io.stimulus_catalog import DatasetStimulusCatalog
from fra.reports.session_report import SessionReportBuilder


class StimulusSessionRunner:
    def __init__(self) -> None:
        self.catalog = DatasetStimulusCatalog()
        self.norm_generator = DatasetNormativeProfileGenerator()
        self.recorder = StimulusReactionRecorder()
        self.pipeline = ReactionAnalysisPipeline()
        self.session_report_builder = SessionReportBuilder()

    def run(
        self,
        dataset: str,
        output_json_path: str,
        output_csv_path: str | None = None,
        stimulus_id: str | None = None,
        category: str | None = None,
        camera_index: int = 0,
        baseline_sec: float = 1.0,
        stimulus_sec: float = 3.0,
        recovery_sec: float = 2.0,
        captured_video_path: str | None = None,
        generated_norm_path: str | None = None,
        headless: bool = False,
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
        video_path = captured_video_path or str(
            Path(output_json_path).with_suffix(".captured.mp4")
        )
        recorded_video = self.recorder.record(
            stimulus_image_path=str(stimulus.metadata["image_path"]),
            output_video_path=video_path,
            camera_index=camera_index,
            baseline_sec=baseline_sec,
            stimulus_sec=stimulus_sec,
            recovery_sec=recovery_sec,
            headless=headless,
        )
        return self.pipeline.run_with_profile(
            video_path=recorded_video,
            stimulus=stimulus,
            normative_profile=normative_profile,
            output_json_path=output_json_path,
            output_csv_path=output_csv_path,
        )

    def run_study(
        self,
        dataset: str,
        count: int,
        output_json_path: str,
        output_csv_path: str | None = None,
        category: str | None = None,
        camera_index: int = 0,
        baseline_sec: float = 1.0,
        stimulus_sec: float = 3.0,
        recovery_sec: float = 2.0,
        artifacts_dir: str | None = None,
        seed: int | None = None,
        headless: bool = False,
    ) -> dict[str, object]:
        rng = random.Random(seed)
        entries = self.catalog.list_entries(dataset=dataset, category=category)
        if not entries:
            raise FileNotFoundError(f"No stimuli found for dataset={dataset} category={category}")
        if count <= 0:
            raise ValueError("count must be greater than zero")

        sample_size = min(count, len(entries))
        selected_entries = rng.sample(entries, k=sample_size)
        base_dir = Path(artifacts_dir) if artifacts_dir else Path(output_json_path).with_suffix("")
        base_dir.mkdir(parents=True, exist_ok=True)

        session_items: list[dict[str, object]] = []
        for index, entry in enumerate(selected_entries, start=1):
            stimulus = self.catalog.get_descriptor(
                dataset=dataset,
                stimulus_id=entry.stimulus_id,
                category=category,
            )
            normative_profile = self.norm_generator.build(
                stimulus=stimulus,
                baseline_sec=baseline_sec,
                stimulus_sec=stimulus_sec,
                recovery_sec=recovery_sec,
            )

            item_prefix = f"{index:02d}_{stimulus.stimulus_id}"
            video_path = str(base_dir / f"{item_prefix}.captured.mp4")
            norm_path = str(base_dir / f"{item_prefix}.generated_norm.json")
            json_report_path = str(base_dir / f"{item_prefix}.report.json")
            csv_report_path = str(base_dir / f"{item_prefix}.timeline.csv")

            self.norm_generator.save(normative_profile, norm_path)
            recorded_video = self.recorder.record(
                stimulus_image_path=str(stimulus.metadata["image_path"]),
                output_video_path=video_path,
                camera_index=camera_index,
                baseline_sec=baseline_sec,
                stimulus_sec=stimulus_sec,
                recovery_sec=recovery_sec,
                headless=headless,
            )
            artifacts = self.pipeline.run_with_profile(
                video_path=recorded_video,
                stimulus=stimulus,
                normative_profile=normative_profile,
                output_json_path=json_report_path,
                output_csv_path=csv_report_path,
                normative_profile_path=norm_path,
            )
            session_items.append(
                self.session_report_builder.build_item(
                    index=index,
                    artifacts=artifacts,
                    json_report_path=json_report_path,
                    csv_report_path=csv_report_path,
                    video_path=recorded_video,
                    norm_path=norm_path,
                )
            )

        summary_payload = self.session_report_builder.build_json(
            dataset=dataset,
            session_items=session_items,
        )
        Path(output_json_path).write_text(
            json.dumps(summary_payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        if output_csv_path:
            self.session_report_builder.build_csv(session_items).to_csv(output_csv_path, index=False)
        return summary_payload
