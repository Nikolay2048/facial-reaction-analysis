from __future__ import annotations

from fra.domain.models import DeviationResult


class DeviationCalculator:
    def calculate(
        self,
        comparison: dict[str, float],
        thresholds: dict[str, float] | None = None,
    ) -> DeviationResult:
        thresholds = thresholds or {}

        amplitude_score = self._normalize_gap(
            comparison["amplitude_gap"],
            thresholds.get("amplitude_tolerance", 1.0),
        )
        latency_score = self._normalize_gap(
            comparison["latency_gap_ms"],
            thresholds.get("latency_tolerance_ms", 1000.0),
        )
        symmetry_score = self._normalize_gap(
            comparison["symmetry_gap"],
            thresholds.get("symmetry_tolerance", 1.0),
        )
        recovery_score = self._normalize_gap(
            comparison["recovery_gap"],
            thresholds.get("recovery_tolerance", 1.0),
        )

        global_score = (
            0.35 * amplitude_score
            + 0.25 * latency_score
            + 0.20 * symmetry_score
            + 0.20 * recovery_score
        )

        warnings = self._build_warnings(comparison, thresholds, global_score)

        return DeviationResult(
            global_score=global_score,
            amplitude_score=amplitude_score,
            latency_score=latency_score,
            symmetry_score=symmetry_score,
            recovery_score=recovery_score,
            confidence=0.0,
            warnings=warnings,
        )

    @staticmethod
    def _normalize_gap(gap: float, tolerance: float) -> float:
        safe_tolerance = tolerance if tolerance > 0 else 1.0
        return max(0.0, min(1.0, gap / safe_tolerance))

    def _build_warnings(
        self,
        comparison: dict[str, float],
        thresholds: dict[str, float],
        global_score: float,
    ) -> list[str]:
        warnings: list[str] = []

        if self._exceeds_threshold(
            comparison["amplitude_gap"],
            thresholds.get("amplitude_tolerance"),
        ):
            warnings.append("Amplitude deviation exceeds the normative tolerance.")

        if self._exceeds_threshold(
            comparison["latency_gap_ms"],
            thresholds.get("latency_tolerance_ms"),
        ):
            warnings.append("Latency deviation exceeds the normative tolerance.")

        if self._exceeds_threshold(
            comparison["symmetry_gap"],
            thresholds.get("symmetry_tolerance"),
        ):
            warnings.append("Facial asymmetry exceeds the normative tolerance.")

        if self._exceeds_threshold(
            comparison["recovery_gap"],
            thresholds.get("recovery_tolerance"),
        ):
            warnings.append("Recovery dynamics deviate from the normative tolerance.")

        if global_score > 0.5:
            warnings.append("High deviation relative to selected normative profile.")
        return warnings

    @staticmethod
    def _exceeds_threshold(value: float, threshold: float | None) -> bool:
        return threshold is not None and threshold > 0 and value > threshold
