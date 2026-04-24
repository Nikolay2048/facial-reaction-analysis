from __future__ import annotations

import numpy as np

from fra.domain.models import NormativeProfile, ReactionProfile


class TemporalAligner:
    def align(
        self,
        actual_profile: ReactionProfile,
        normative_profile: NormativeProfile,
    ) -> tuple[ReactionProfile, NormativeProfile]:
        if not actual_profile.timestamps_ms or not actual_profile.features:
            return actual_profile, normative_profile
        if not normative_profile.timestamps_ms or not normative_profile.expected_features:
            return actual_profile, normative_profile

        target_timestamps = [float(timestamp) for timestamp in normative_profile.timestamps_ms]
        aligned_actual = ReactionProfile(
            stimulus_id=actual_profile.stimulus_id,
            timestamps_ms=target_timestamps,
            features=self._resample_feature_series(
                source_timestamps=actual_profile.timestamps_ms,
                source_features=actual_profile.features,
                target_timestamps=target_timestamps,
            ),
            metadata={
                **actual_profile.metadata,
                "aligned_to": "normative_timestamps",
                "alignment_method": "linear_interpolation",
            },
        )
        aligned_actual.onset_ms, aligned_actual.peak_ms, aligned_actual.recovery_ms = (
            self._derive_phase_markers(aligned_actual)
        )

        aligned_normative = NormativeProfile(
            stimulus_category=normative_profile.stimulus_category,
            expected_features=self._resample_feature_series(
                source_timestamps=normative_profile.timestamps_ms,
                source_features=normative_profile.expected_features,
                target_timestamps=target_timestamps,
            ),
            timestamps_ms=target_timestamps,
            thresholds=normative_profile.thresholds,
            metadata={
                **normative_profile.metadata,
                "alignment_method": "reference_grid",
            },
        )
        return aligned_actual, aligned_normative

    def _resample_feature_series(
        self,
        source_timestamps: list[float],
        source_features: list[dict[str, float]],
        target_timestamps: list[float],
    ) -> list[dict[str, float]]:
        if not source_timestamps or not source_features:
            return []

        ordered_pairs = sorted(
            zip(source_timestamps, source_features, strict=False),
            key=lambda item: item[0],
        )
        ordered_timestamps = np.array([float(item[0]) for item in ordered_pairs], dtype=float)
        ordered_features = [item[1] for item in ordered_pairs]
        feature_names = self._collect_feature_names(ordered_features)

        resampled_rows: list[dict[str, float]] = []
        for target_timestamp in target_timestamps:
            row: dict[str, float] = {}
            for feature_name in feature_names:
                source_values = np.array(
                    [float(feature_map.get(feature_name, 0.0)) for feature_map in ordered_features],
                    dtype=float,
                )
                row[feature_name] = float(
                    np.interp(float(target_timestamp), ordered_timestamps, source_values)
                )
            resampled_rows.append(row)
        return resampled_rows

    @staticmethod
    def _collect_feature_names(feature_series: list[dict[str, float]]) -> list[str]:
        ordered_names: list[str] = []
        for feature_map in feature_series:
            for name in feature_map:
                if name not in ordered_names:
                    ordered_names.append(name)
        return ordered_names

    @staticmethod
    def _derive_phase_markers(reaction_profile: ReactionProfile) -> tuple[float | None, float | None, float | None]:
        if not reaction_profile.features or not reaction_profile.timestamps_ms:
            return None, None, None

        threshold = 0.05
        intensities = [
            float(feature_map.get("response_intensity", 0.0))
            for feature_map in reaction_profile.features
        ]
        timestamps = reaction_profile.timestamps_ms

        onset_ms = next(
            (timestamp for timestamp, intensity in zip(timestamps, intensities, strict=False) if intensity > threshold),
            timestamps[0],
        )
        peak_index = max(range(len(intensities)), key=lambda idx: intensities[idx])
        peak_ms = timestamps[peak_index]
        recovery_ms = next(
            (
                timestamp
                for timestamp, intensity in zip(timestamps[peak_index + 1 :], intensities[peak_index + 1 :], strict=False)
                if intensity <= threshold
            ),
            timestamps[-1],
        )
        return onset_ms, peak_ms, recovery_ms
