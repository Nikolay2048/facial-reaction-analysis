from __future__ import annotations

from fra.domain.models import FacialFeatureVector, ReactionProfile


class ReactionProfileBuilder:
    def build(
        self,
        stimulus_description: str,
        feature_vectors: list[FacialFeatureVector],
    ) -> ReactionProfile:
        timestamps = [item.timestamp_ms for item in feature_vectors]
        features = [
            {
                "eye_openness": item.eye_openness,
                "eyebrow_raise": item.eyebrow_raise,
                "mouth_openness": item.mouth_openness,
                "lip_corner_movement": item.lip_corner_movement,
                "facial_asymmetry": item.facial_asymmetry,
                "response_intensity": item.response_intensity,
            }
            for item in feature_vectors
        ]

        onset_ms = None
        peak_ms = None
        recovery_ms = None
        if feature_vectors:
            onset_ms = next(
                (item.timestamp_ms for item in feature_vectors if item.response_intensity > 0.05),
                feature_vectors[0].timestamp_ms,
            )
            peak_vector = max(feature_vectors, key=lambda item: item.response_intensity)
            peak_ms = peak_vector.timestamp_ms
            recovery_ms = next(
                (
                    item.timestamp_ms
                    for item in feature_vectors
                    if peak_ms is not None
                    and item.timestamp_ms > peak_ms
                    and item.response_intensity <= 0.05
                ),
                feature_vectors[-1].timestamp_ms,
            )

        return ReactionProfile(
            stimulus_id=stimulus_description,
            timestamps_ms=timestamps,
            features=features,
            onset_ms=onset_ms,
            peak_ms=peak_ms,
            recovery_ms=recovery_ms,
            metadata={"feature_count": len(feature_vectors)},
        )
