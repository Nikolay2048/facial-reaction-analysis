from __future__ import annotations

import json
import math
from pathlib import Path

from fra.domain.models import NormativeProfile, StimulusDescriptor


class DatasetNormativeProfileGenerator:
    def build(
        self,
        stimulus: StimulusDescriptor,
        baseline_sec: float,
        stimulus_sec: float,
        recovery_sec: float,
    ) -> NormativeProfile:
        valence_mean = float(stimulus.metadata.get("valence_mean", 50.0))
        arousal_mean = float(stimulus.metadata.get("arousal_mean", 50.0))
        valence_sd = float(stimulus.metadata.get("valence_sd", 0.0))
        arousal_sd = float(stimulus.metadata.get("arousal_sd", 0.0))

        valence_norm = self._normalize_valence(stimulus.source_dataset, valence_mean)
        arousal_norm = self._normalize_arousal(stimulus.source_dataset, arousal_mean)
        emotional_bias = abs((2.0 * valence_norm) - 1.0)

        total_ms = int((baseline_sec + stimulus_sec + recovery_sec) * 1000.0)
        onset_ms = int((baseline_sec * 1000.0) + (550.0 - 250.0 * arousal_norm))
        peak_ms = min(
            total_ms - int(recovery_sec * 500.0),
            onset_ms + int(350.0 + 700.0 * (1.0 - arousal_norm)),
        )
        recovery_ms = min(
            total_ms,
            peak_ms + int(600.0 + 800.0 * arousal_norm),
        )
        timestamps_ms = self._build_timestamps(total_ms)

        amplitude = 0.06 + (0.20 * arousal_norm) + (0.10 * emotional_bias)
        polarity = stimulus.category.lower()
        expected_features = []
        for timestamp_ms in timestamps_ms:
            intensity = self._intensity_curve(
                timestamp_ms=timestamp_ms,
                onset_ms=onset_ms,
                peak_ms=peak_ms,
                recovery_ms=recovery_ms,
                amplitude=amplitude,
            )
            feature_map = self._build_feature_map(
                intensity=intensity,
                polarity=polarity,
                arousal_norm=arousal_norm,
            )
            expected_features.append(feature_map)

        tolerance_scale = 1.0 + min(1.0, (valence_sd + arousal_sd) / 40.0)
        thresholds = {
            "amplitude_tolerance": round(0.08 * tolerance_scale, 4),
            "latency_tolerance_ms": round(220.0 + 180.0 * tolerance_scale, 2),
            "symmetry_tolerance": round(0.05 * tolerance_scale, 4),
            "recovery_tolerance": round(0.15 * tolerance_scale, 4),
        }
        return NormativeProfile(
            stimulus_category=polarity,
            expected_features=expected_features,
            timestamps_ms=[float(item) for item in timestamps_ms],
            thresholds=thresholds,
            metadata={
                "norm_source": "dataset_heuristic_template",
                "source_dataset": stimulus.source_dataset or "unknown",
                "valence_mean": valence_mean,
                "arousal_mean": arousal_mean,
                "valence_sd": valence_sd,
                "arousal_sd": arousal_sd,
                "baseline_sec": baseline_sec,
                "stimulus_sec": stimulus_sec,
                "recovery_sec": recovery_sec,
                "onset_ms": onset_ms,
                "peak_ms": peak_ms,
                "recovery_ms": recovery_ms,
            },
        )

    def save(self, normative_profile: NormativeProfile, output_path: str) -> str:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "stimulus_category": normative_profile.stimulus_category,
            "timestamps_ms": normative_profile.timestamps_ms,
            "expected_features": normative_profile.expected_features,
            "thresholds": normative_profile.thresholds,
            "metadata": normative_profile.metadata,
        }
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return str(path)

    @staticmethod
    def _build_timestamps(total_ms: int, step_ms: int = 200) -> list[int]:
        timestamps = list(range(0, total_ms + step_ms, step_ms))
        if timestamps[-1] != total_ms:
            timestamps.append(total_ms)
        return timestamps

    @staticmethod
    def _normalize_valence(dataset: str | None, value: float) -> float:
        if dataset == "oasis":
            return max(0.0, min(1.0, (value - 1.0) / 6.0))
        return max(0.0, min(1.0, value / 100.0))

    @staticmethod
    def _normalize_arousal(dataset: str | None, value: float) -> float:
        if dataset == "oasis":
            return max(0.0, min(1.0, (value - 1.0) / 6.0))
        return max(0.0, min(1.0, value / 100.0))

    def _intensity_curve(
        self,
        timestamp_ms: int,
        onset_ms: int,
        peak_ms: int,
        recovery_ms: int,
        amplitude: float,
    ) -> float:
        if timestamp_ms <= onset_ms:
            return 0.01
        if timestamp_ms <= peak_ms:
            ratio = (timestamp_ms - onset_ms) / max(1.0, peak_ms - onset_ms)
            return 0.01 + amplitude * math.sin((math.pi / 2.0) * ratio)
        if timestamp_ms <= recovery_ms:
            ratio = (timestamp_ms - peak_ms) / max(1.0, recovery_ms - peak_ms)
            return 0.01 + amplitude * max(0.0, 1.0 - ratio)
        return 0.01

    @staticmethod
    def _build_feature_map(
        intensity: float,
        polarity: str,
        arousal_norm: float,
    ) -> dict[str, float]:
        positive = polarity == "positive"
        negative = polarity == "negative"

        eyebrow_raise = intensity * (0.55 if negative else 0.45)
        eye_openness = intensity * (0.60 if negative else 0.35 + 0.15 * arousal_norm)
        mouth_openness = intensity * (0.45 if negative else 0.30)
        lip_corner_movement = intensity * (0.60 if positive else 0.10)
        facial_asymmetry = max(0.01, intensity * 0.08)

        return {
            "eye_openness": round(eye_openness, 4),
            "eyebrow_raise": round(eyebrow_raise, 4),
            "mouth_openness": round(mouth_openness, 4),
            "lip_corner_movement": round(lip_corner_movement, 4),
            "facial_asymmetry": round(facial_asymmetry, 4),
            "response_intensity": round(intensity, 4),
        }
