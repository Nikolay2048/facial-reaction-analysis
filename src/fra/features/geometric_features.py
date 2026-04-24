from __future__ import annotations

import numpy as np

from fra.domain.models import FacialFeatureVector, FrameData


class GeometricFeatureExtractor:
    def extract(self, frame_data: FrameData) -> FacialFeatureVector:
        if frame_data.landmarks is None:
            raise ValueError("Landmarks are required to extract geometric features.")

        points = frame_data.landmarks
        xs = points[:, 0]
        ys = points[:, 1]
        face_width = max(float(xs.max() - xs.min()), 1e-6)
        face_height = max(float(ys.max() - ys.min()), 1e-6)

        eye_openness = self._vertical_distance(points, 159, 145) / face_height
        eyebrow_raise = self._vertical_distance(points, 105, 159) / face_height
        mouth_openness = self._vertical_distance(points, 13, 14) / face_height
        lip_corner_movement = self._horizontal_distance(points, 61, 291) / face_width
        facial_asymmetry = abs(
            self._vertical_distance(points, 159, 145) - self._vertical_distance(points, 386, 374)
        ) / face_height

        response_intensity = (
            0.30 * eyebrow_raise
            + 0.25 * eye_openness
            + 0.30 * mouth_openness
            + 0.15 * abs(lip_corner_movement)
        )

        return FacialFeatureVector(
            frame_index=frame_data.frame_index,
            timestamp_ms=frame_data.timestamp_ms,
            eye_openness=eye_openness,
            eyebrow_raise=eyebrow_raise,
            mouth_openness=mouth_openness,
            lip_corner_movement=lip_corner_movement,
            facial_asymmetry=facial_asymmetry,
            response_intensity=response_intensity,
        )

    @staticmethod
    def _vertical_distance(points: np.ndarray, index_a: int, index_b: int) -> float:
        return float(abs(points[index_a][1] - points[index_b][1]))

    @staticmethod
    def _horizontal_distance(points: np.ndarray, index_a: int, index_b: int) -> float:
        return float(abs(points[index_a][0] - points[index_b][0]))
