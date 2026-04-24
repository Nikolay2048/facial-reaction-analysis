from __future__ import annotations

from fra.domain.models import FacialFeatureVector


class FeatureNormalizer:
    def normalize(self, feature_vectors: list[FacialFeatureVector]) -> list[FacialFeatureVector]:
        if not feature_vectors:
            return feature_vectors

        baseline = feature_vectors[0]
        for feature in feature_vectors:
            feature.eye_openness = max(0.0, feature.eye_openness - baseline.eye_openness)
            feature.eyebrow_raise = max(0.0, feature.eyebrow_raise - baseline.eyebrow_raise)
            feature.mouth_openness = max(0.0, feature.mouth_openness - baseline.mouth_openness)
            feature.lip_corner_movement = feature.lip_corner_movement - baseline.lip_corner_movement
            feature.facial_asymmetry = max(0.0, feature.facial_asymmetry)
            feature.response_intensity = max(0.0, feature.response_intensity - baseline.response_intensity)
        return feature_vectors
