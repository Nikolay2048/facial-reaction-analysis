from __future__ import annotations

import pandas as pd

from fra.domain.models import AnalysisArtifacts


class SessionReportBuilder:
    def build_json(
        self,
        dataset: str,
        session_items: list[dict[str, object]],
    ) -> dict[str, object]:
        if not session_items:
            return {
                "dataset": dataset,
                "stimulus_count": 0,
                "mean_global_score": 0.0,
                "mean_confidence": 0.0,
                "mean_amplitude_score": 0.0,
                "mean_latency_score": 0.0,
                "mean_symmetry_score": 0.0,
                "mean_recovery_score": 0.0,
                "alignment_counts": {},
                "items": [],
            }

        rows = [item["summary"] for item in session_items]
        frame = pd.DataFrame(rows)
        alignment_counts = (
            frame["alignment"].value_counts().to_dict()
            if "alignment" in frame.columns
            else {}
        )
        return {
            "dataset": dataset,
            "stimulus_count": int(len(rows)),
            "mean_global_score": float(frame["global_score"].mean()),
            "mean_confidence": float(frame["confidence"].mean()),
            "mean_amplitude_score": float(frame["amplitude_score"].mean()),
            "mean_latency_score": float(frame["latency_score"].mean()),
            "mean_symmetry_score": float(frame["symmetry_score"].mean()),
            "mean_recovery_score": float(frame["recovery_score"].mean()),
            "alignment_counts": {str(key): int(value) for key, value in alignment_counts.items()},
            "items": rows,
        }

    def build_csv(self, session_items: list[dict[str, object]]) -> pd.DataFrame:
        rows = [item["summary"] for item in session_items]
        return pd.DataFrame(rows)

    def build_item(
        self,
        index: int,
        artifacts: AnalysisArtifacts,
        json_report_path: str,
        csv_report_path: str | None,
        video_path: str,
        norm_path: str,
    ) -> dict[str, object]:
        interpretation = artifacts.interpretation
        return {
            "summary": {
                "index": index,
                "stimulus_id": artifacts.stimulus.stimulus_id,
                "stimulus_description": artifacts.stimulus.description,
                "stimulus_category": artifacts.stimulus.category,
                "source_dataset": artifacts.stimulus.source_dataset,
                "expected_stimulus_emotions": ",".join(
                    interpretation.get("expected_stimulus_emotions", [])
                ),
                "expected_observed_emotions": ",".join(
                    interpretation.get("expected_observed_emotions", [])
                ),
                "actual_observed_emotion": interpretation.get("actual_observed_emotion", "neutral"),
                "alignment": interpretation.get("alignment", "unknown"),
                "global_score": artifacts.deviation_result.global_score,
                "amplitude_score": artifacts.deviation_result.amplitude_score,
                "latency_score": artifacts.deviation_result.latency_score,
                "symmetry_score": artifacts.deviation_result.symmetry_score,
                "recovery_score": artifacts.deviation_result.recovery_score,
                "confidence": artifacts.deviation_result.confidence,
                "json_report_path": json_report_path,
                "csv_report_path": csv_report_path or "",
                "captured_video_path": video_path,
                "generated_norm_path": norm_path,
            }
        }
