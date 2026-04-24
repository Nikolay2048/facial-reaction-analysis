from __future__ import annotations

import numpy as np


class FaceDetector:
    def detect(self, image: np.ndarray | None) -> bool:
        return image is not None
