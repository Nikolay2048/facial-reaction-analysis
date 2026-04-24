from __future__ import annotations

from pathlib import Path

from fra.domain.models import FrameData


class VideoReader:
    def read(self, video_path: str) -> list[FrameData]:
        import cv2

        path = Path(video_path)
        capture = cv2.VideoCapture(str(path))
        if not capture.isOpened():
            raise FileNotFoundError(f"Cannot open video: {video_path}")

        fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
        frames: list[FrameData] = []
        frame_index = 0

        while True:
            success, frame = capture.read()
            if not success:
                break

            timestamp_ms = (frame_index / fps) * 1000.0
            frames.append(
                FrameData(
                    frame_index=frame_index,
                    timestamp_ms=timestamp_ms,
                    image=frame,
                    face_detected=False,
                )
            )
            frame_index += 1

        capture.release()
        return frames
