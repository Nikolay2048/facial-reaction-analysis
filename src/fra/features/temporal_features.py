from __future__ import annotations

from fra.domain.models import FacialFeatureVector


class TemporalFeatureExtractor:
    def enrich(self, feature_vectors: list[FacialFeatureVector]) -> list[FacialFeatureVector]:
        if not feature_vectors:
            return feature_vectors

        previous_intensity = feature_vectors[0].response_intensity
        for feature in feature_vectors[1:]:
            delta = max(0.0, feature.response_intensity - previous_intensity)
            feature.response_intensity += 0.1 * delta
            previous_intensity = feature.response_intensity
        return feature_vectors
