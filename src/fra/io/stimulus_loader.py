from __future__ import annotations

from fra.domain.models import StimulusDescriptor


class StimulusDescriptorLoader:
    def load(self, description: str) -> StimulusDescriptor:
        normalized = description.strip()
        category = self._infer_category(normalized.lower())
        stimulus_id = normalized[:48].replace(" ", "_") or "unknown"
        return StimulusDescriptor(
            stimulus_id=stimulus_id,
            description=normalized,
            category=category,
            source_dataset=None,
            metadata={"source": "cli"},
        )

    @staticmethod
    def _infer_category(description: str) -> str:
        positive_markers = ("pleasant", "reward", "happy", "joy", "surprise", "positive")
        negative_markers = ("threat", "fear", "sad", "anger", "negative", "aversive")
        neutral_markers = ("neutral", "baseline", "control")

        if any(marker in description for marker in positive_markers):
            return "positive"
        if any(marker in description for marker in negative_markers):
            return "negative"
        if any(marker in description for marker in neutral_markers):
            return "neutral"
        return "generic"
