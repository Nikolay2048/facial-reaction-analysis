from __future__ import annotations

from fra.domain.models import FrameData


class FrameQualityAssessor:
    def assess(self, frame_data: FrameData) -> FrameData:
        import cv2
        import numpy as np

        if frame_data.image is None:
            frame_data.quality_score = 0.0
            frame_data.quality_flags.append("empty_frame")
            return frame_data

        gray = cv2.cvtColor(frame_data.image, cv2.COLOR_BGR2GRAY)
        brightness = float(np.mean(gray) / 255.0)
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var() / 1000.0)

        score = min(1.0, 0.5 * brightness + 0.5 * min(sharpness, 1.0))
        flags: list[str] = []
        if not frame_data.face_detected:
            flags.append("no_face")
        if brightness < 0.2:
            flags.append("low_brightness")
        if sharpness < 0.05:
            flags.append("low_sharpness")

        frame_data.quality_score = score
        frame_data.quality_flags = flags
        return frame_data
