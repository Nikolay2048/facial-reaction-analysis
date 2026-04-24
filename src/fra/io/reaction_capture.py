from __future__ import annotations

import time
from pathlib import Path


class StimulusReactionRecorder:
    def record(
        self,
        stimulus_image_path: str,
        output_video_path: str,
        camera_index: int,
        baseline_sec: float,
        stimulus_sec: float,
        recovery_sec: float,
        headless: bool = False,
    ) -> str:
        import cv2
        import numpy as np

        capture = cv2.VideoCapture(camera_index)
        if not capture.isOpened():
            raise RuntimeError(f"Cannot open camera index {camera_index}")

        fps = capture.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 1.0:
            fps = 25.0

        success, first_frame = capture.read()
        if not success or first_frame is None:
            capture.release()
            raise RuntimeError("Cannot read the first frame from the camera.")

        height, width = first_frame.shape[:2]
        output_path = Path(output_video_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        writer = cv2.VideoWriter(
            str(output_path),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height),
        )
        if not writer.isOpened():
            capture.release()
            raise RuntimeError(f"Cannot open video writer for {output_video_path}")

        stimulus_image = cv2.imread(stimulus_image_path)
        if stimulus_image is None:
            writer.release()
            capture.release()
            raise FileNotFoundError(f"Cannot read stimulus image: {stimulus_image_path}")

        stimulus_canvas = self._fit_to_canvas(stimulus_image, width, height)
        baseline_canvas = self._build_message_canvas(
            width=width,
            height=height,
            message="Prepare for stimulus",
        )
        recovery_canvas = self._build_message_canvas(
            width=width,
            height=height,
            message="Recovery",
        )

        try:
            writer.write(first_frame)
            if not headless:
                cv2.imshow("Reaction Capture", first_frame)
                cv2.waitKey(1)

            self._record_phase(
                capture=capture,
                writer=writer,
                display_frame=baseline_canvas,
                duration_sec=baseline_sec,
                headless=headless,
            )
            self._record_phase(
                capture=capture,
                writer=writer,
                display_frame=stimulus_canvas,
                duration_sec=stimulus_sec,
                headless=headless,
            )
            self._record_phase(
                capture=capture,
                writer=writer,
                display_frame=recovery_canvas,
                duration_sec=recovery_sec,
                headless=headless,
            )
        finally:
            writer.release()
            capture.release()
            if not headless:
                cv2.destroyAllWindows()

        return str(output_path)

    def _record_phase(
        self,
        capture,
        writer,
        display_frame,
        duration_sec: float,
        headless: bool,
    ) -> None:
        import cv2

        end_time = time.perf_counter() + duration_sec
        while time.perf_counter() < end_time:
            success, frame = capture.read()
            if not success or frame is None:
                continue
            writer.write(frame)
            if not headless:
                cv2.imshow("Reaction Capture", display_frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

    @staticmethod
    def _fit_to_canvas(image, width: int, height: int):
        import cv2
        import numpy as np

        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        image_height, image_width = image.shape[:2]
        scale = min(width / image_width, height / image_height)
        target_width = max(1, int(image_width * scale))
        target_height = max(1, int(image_height * scale))
        resized = cv2.resize(image, (target_width, target_height))
        y_offset = (height - target_height) // 2
        x_offset = (width - target_width) // 2
        canvas[y_offset : y_offset + target_height, x_offset : x_offset + target_width] = resized
        return canvas

    @staticmethod
    def _build_message_canvas(width: int, height: int, message: str):
        import cv2
        import numpy as np

        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        cv2.putText(
            canvas,
            message,
            (max(10, width // 8), max(40, height // 2)),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        return canvas
