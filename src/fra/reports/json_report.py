from __future__ import annotations

from fra.domain.models import DeviationResult, FrameData, NormativeProfile, ReactionProfile, StimulusDescriptor
from fra.domain.schemas import (
    DeviationSchema,
    InterpretationSchema,
    NormativeReferenceSchema,
    QualityReportSchema,
    ReactionProfileSchema,
    ReportSchema,
    StimulusSchema,
)


class JSONReportBuilder:
    def build(
        self,
        stimulus: StimulusDescriptor,
        normative_profile: NormativeProfile,
        reaction_profile: ReactionProfile,
        deviation_result: DeviationResult,
        interpretation: dict[str, object],
        frame_data: list[FrameData],
        video_path: str,
    ) -> dict:
        processed_frames = len(frame_data)
        valid_frames = sum(1 for item in frame_data if item.face_detected)
        tracking_success_rate = valid_frames / processed_frames if processed_frames else 0.0

        report = ReportSchema(
            input={"video_path": video_path, "module": "fra"},
            stimulus=StimulusSchema(
                stimulus_id=stimulus.stimulus_id,
                description=stimulus.description,
                category=stimulus.category,
                source_dataset=stimulus.source_dataset,
            ),
            quality=QualityReportSchema(
                processed_frames=processed_frames,
                valid_frames=valid_frames,
                tracking_success_rate=tracking_success_rate,
            ),
            normative_reference=NormativeReferenceSchema(
                stimulus_category=normative_profile.stimulus_category,
                thresholds=normative_profile.thresholds,
                metadata=normative_profile.metadata,
            ),
            reaction_profile=ReactionProfileSchema(
                onset_ms=reaction_profile.onset_ms,
                peak_ms=reaction_profile.peak_ms,
                recovery_ms=reaction_profile.recovery_ms,
                timestamps_ms=reaction_profile.timestamps_ms,
                features=reaction_profile.features,
                metadata=reaction_profile.metadata,
            ),
            deviation=DeviationSchema(
                global_score=deviation_result.global_score,
                amplitude_score=deviation_result.amplitude_score,
                latency_score=deviation_result.latency_score,
                symmetry_score=deviation_result.symmetry_score,
                recovery_score=deviation_result.recovery_score,
                confidence=deviation_result.confidence,
            ),
            interpretation=InterpretationSchema.model_validate(interpretation),
            warnings=deviation_result.warnings,
        )
        return report.model_dump(mode="json")
