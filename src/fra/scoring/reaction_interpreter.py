from __future__ import annotations

from fra.domain.models import DeviationResult, NormativeProfile, ReactionProfile, StimulusDescriptor


ARTEMIS_TO_OBSERVED = {
    "amusement": ["happy", "surprise"],
    "contentment": ["happy", "neutral"],
    "excitement": ["surprise", "happy"],
    "awe": ["surprise", "happy"],
    "fear": ["fear", "surprise"],
    "sadness": ["sad", "neutral"],
    "disgust": ["disgust", "angry"],
    "anger": ["angry", "disgust"],
    "something else": ["neutral", "surprise"],
}


class ReactionInterpreter:
    def interpret(
        self,
        stimulus: StimulusDescriptor,
        reaction_profile: ReactionProfile,
        normative_profile: NormativeProfile,
        deviation_result: DeviationResult,
        comparison: dict[str, float],
    ) -> dict[str, object]:
        peak_features = self._get_peak_features(reaction_profile)
        actual_response_label = self._infer_observed_emotion(peak_features)
        expected_stimulus_emotions = list(
            stimulus.metadata.get("expected_stimulus_emotions", [])
        )
        expected_observed_emotions = self._expected_observed_emotions(
            stimulus=stimulus,
            normative_profile=normative_profile,
        )
        alignment = (
            "aligned"
            if actual_response_label in expected_observed_emotions
            else "deviating"
        )

        return {
            "stimulus_source_dataset": stimulus.source_dataset,
            "stimulus_category": stimulus.category,
            "expected_stimulus_emotions": expected_stimulus_emotions,
            "expected_observed_emotions": expected_observed_emotions,
            "reference_utterances": list(stimulus.metadata.get("utterance_examples", [])),
            "actual_observed_emotion": actual_response_label,
            "peak_response_features": peak_features,
            "alignment": alignment,
            "summary": self._build_summary(
                expected_observed_emotions=expected_observed_emotions,
                actual_response_label=actual_response_label,
                deviation_result=deviation_result,
                comparison=comparison,
            ),
        }

    def _expected_observed_emotions(
        self,
        stimulus: StimulusDescriptor,
        normative_profile: NormativeProfile,
    ) -> list[str]:
        expected = stimulus.metadata.get("expected_observed_emotions")
        if isinstance(expected, list) and expected:
            return [str(item) for item in expected]

        artemis_emotions = stimulus.metadata.get("expected_stimulus_emotions", [])
        mapped: list[str] = []
        for emotion in artemis_emotions:
            for observed in ARTEMIS_TO_OBSERVED.get(str(emotion), []):
                if observed not in mapped:
                    mapped.append(observed)
        if mapped:
            return mapped

        fallback = normative_profile.stimulus_category.lower()
        if fallback == "positive":
            return ["happy", "surprise"]
        if fallback == "negative":
            return ["fear", "sad", "disgust", "angry"]
        return ["neutral"]

    @staticmethod
    def _get_peak_features(reaction_profile: ReactionProfile) -> dict[str, float]:
        if not reaction_profile.features:
            return {}
        return max(
            reaction_profile.features,
            key=lambda feature_map: feature_map.get("response_intensity", 0.0),
        )

    def _infer_observed_emotion(self, peak_features: dict[str, float]) -> str:
        if not peak_features:
            return "neutral"

        lip = peak_features.get("lip_corner_movement", 0.0)
        mouth = peak_features.get("mouth_openness", 0.0)
        eye = peak_features.get("eye_openness", 0.0)
        brow = peak_features.get("eyebrow_raise", 0.0)
        asym = peak_features.get("facial_asymmetry", 0.0)
        intensity = peak_features.get("response_intensity", 0.0)

        if lip >= 0.06 and intensity >= 0.08:
            return "happy"
        if mouth >= 0.10 and eye >= 0.06 and brow >= 0.05:
            return "surprise"
        if eye >= 0.07 and brow >= 0.06 and mouth >= 0.05:
            return "fear"
        if asym >= 0.06 and mouth < 0.05:
            return "disgust"
        if asym >= 0.04 and lip < 0.02 and intensity >= 0.05:
            return "angry"
        if intensity <= 0.03:
            return "neutral"
        return "sad"

    @staticmethod
    def _build_summary(
        expected_observed_emotions: list[str],
        actual_response_label: str,
        deviation_result: DeviationResult,
        comparison: dict[str, float],
    ) -> str:
        expected_text = ", ".join(expected_observed_emotions) if expected_observed_emotions else "neutral"
        return (
            f"Expected visible reaction classes: {expected_text}. "
            f"Observed reaction is closest to '{actual_response_label}'. "
            f"Global deviation={deviation_result.global_score:.3f}, "
            f"amplitude_gap={comparison.get('amplitude_gap', 0.0):.3f}, "
            f"latency_gap_ms={comparison.get('latency_gap_ms', 0.0):.1f}, "
            f"symmetry_gap={comparison.get('symmetry_gap', 0.0):.3f}, "
            f"recovery_gap={comparison.get('recovery_gap', 0.0):.3f}."
        )
