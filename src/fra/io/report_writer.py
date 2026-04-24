from __future__ import annotations

import json
from pathlib import Path

from fra.domain.models import DeviationResult, FrameData, NormativeProfile, ReactionProfile, StimulusDescriptor
from fra.reports.csv_report import CSVReportBuilder
from fra.reports.json_report import JSONReportBuilder


class ReportWriter:
    def __init__(self) -> None:
        self.json_builder = JSONReportBuilder()
        self.csv_builder = CSVReportBuilder()

    def write(
        self,
        output_json_path: str,
        output_csv_path: str | None,
        stimulus: StimulusDescriptor,
        normative_profile: NormativeProfile,
        reaction_profile: ReactionProfile,
        deviation_result: DeviationResult,
        interpretation: dict[str, object],
        frame_data: list[FrameData],
        video_path: str,
    ) -> None:
        json_report = self.json_builder.build(
            stimulus=stimulus,
            normative_profile=normative_profile,
            reaction_profile=reaction_profile,
            deviation_result=deviation_result,
            interpretation=interpretation,
            frame_data=frame_data,
            video_path=video_path,
        )
        Path(output_json_path).write_text(
            json.dumps(json_report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        if output_csv_path:
            csv_frame = self.csv_builder.build(reaction_profile)
            csv_frame.to_csv(output_csv_path, index=False)

    def export(self, input_report_path: Path, output_format: str, output_path: Path) -> None:
        payload = json.loads(input_report_path.read_text(encoding="utf-8"))
        if output_format == "json":
            output_path.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            return

        csv_frame = self.csv_builder.build_from_report(payload)
        csv_frame.to_csv(output_path, index=False)
