from __future__ import annotations

import numpy as np

from fra.domain.models import FrameData


class FaceLandmarkTracker:
    def __init__(self) -> None:
        import mediapipe as mp

        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def process(self, frame_data: FrameData) -> FrameData:
        import cv2

        if frame_data.image is None:
            return frame_data

        rgb = cv2.cvtColor(frame_data.image, cv2.COLOR_BGR2RGB)
        result = self._face_mesh.process(rgb)
        if not result.multi_face_landmarks:
            frame_data.face_detected = False
            return frame_data

        landmarks = result.multi_face_landmarks[0].landmark
        frame_data.face_detected = True
        frame_data.landmarks = np.array([[lm.x, lm.y, lm.z] for lm in landmarks], dtype=float)
        return frame_data
