from __future__ import annotations

from fra.domain.models import FacialFeatureVector, FrameData


class ConfidenceEstimator:
    def estimate(
        self,
        frame_data: list[FrameData],
        feature_vectors: list[FacialFeatureVector],
    ) -> float:
        if not frame_data:
            return 0.0

        valid_frames = sum(1 for frame in frame_data if frame.face_detected)
        tracking_ratio = valid_frames / len(frame_data)
        mean_quality = sum(frame.quality_score for frame in frame_data) / len(frame_data)
        feature_ratio = min(1.0, len(feature_vectors) / max(1, len(frame_data)))
        return max(0.0, min(1.0, 0.5 * tracking_ratio + 0.3 * mean_quality + 0.2 * feature_ratio))
