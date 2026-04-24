from __future__ import annotations

from fra.domain.models import NormativeProfile, ReactionProfile


class ProfileComparator:
    def compare(
        self,
        actual_profile: ReactionProfile,
        normative_profile: NormativeProfile,
    ) -> dict[str, float]:
        actual_peak = max(
            (feature["response_intensity"] for feature in actual_profile.features),
            default=0.0,
        )
        normative_peak = max(
            (feature["response_intensity"] for feature in normative_profile.expected_features),
            default=0.0,
        )
        amplitude_gap = abs(actual_peak - normative_peak)

        latency_gap = 0.0
        normative_peak_ms = self._get_peak_timestamp(
            normative_profile.timestamps_ms,
            normative_profile.expected_features,
        )
        if actual_profile.peak_ms is not None and normative_peak_ms is not None:
            latency_gap = abs(actual_profile.peak_ms - normative_peak_ms)

        actual_symmetry = max(
            (feature.get("facial_asymmetry", 0.0) for feature in actual_profile.features),
            default=0.0,
        )
        normative_symmetry = max(
            (feature.get("facial_asymmetry", 0.0) for feature in normative_profile.expected_features),
            default=0.0,
        )
        symmetry_gap = abs(actual_symmetry - normative_symmetry)

        recovery_gap = 0.0
        normative_recovery_ms = self._get_recovery_timestamp(
            normative_profile.timestamps_ms,
            normative_profile.expected_features,
        )
        if (
            actual_profile.recovery_ms is not None
            and actual_profile.peak_ms is not None
            and normative_peak_ms is not None
            and normative_recovery_ms is not None
        ):
            actual_recovery = actual_profile.recovery_ms - actual_profile.peak_ms
            normative_recovery = normative_recovery_ms - normative_peak_ms
            recovery_gap = abs(actual_recovery - normative_recovery) / 1000.0

        return {
            "amplitude_gap": amplitude_gap,
            "latency_gap_ms": latency_gap,
            "symmetry_gap": symmetry_gap,
            "recovery_gap": recovery_gap,
        }

    @staticmethod
    def _get_peak_timestamp(
        timestamps_ms: list[float],
        features: list[dict[str, float]],
    ) -> float | None:
        if not timestamps_ms or not features:
            return None
        peak_index = max(
            range(len(features)),
            key=lambda idx: features[idx].get("response_intensity", 0.0),
        )
        return timestamps_ms[peak_index]

    def _get_recovery_timestamp(
        self,
        timestamps_ms: list[float],
        features: list[dict[str, float]],
    ) -> float | None:
        peak_ms = self._get_peak_timestamp(timestamps_ms, features)
        if peak_ms is None:
            return None

        threshold = 0.05
        peak_index = timestamps_ms.index(peak_ms)
        for timestamp_ms, feature_map in zip(
            timestamps_ms[peak_index + 1 :],
            features[peak_index + 1 :],
            strict=False,
        ):
            if feature_map.get("response_intensity", 0.0) <= threshold:
                return timestamp_ms
        return timestamps_ms[-1]
