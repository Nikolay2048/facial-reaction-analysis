from __future__ import annotations

from pathlib import Path

from fra.domain.models import AnalysisArtifacts, NormativeProfile, StimulusDescriptor
from fra.features.geometric_features import GeometricFeatureExtractor
from fra.features.normalizer import FeatureNormalizer
from fra.features.temporal_features import TemporalFeatureExtractor
from fra.io.normative_loader import NormativeProfileLoader
from fra.io.report_writer import ReportWriter
from fra.io.stimulus_loader import StimulusDescriptorLoader
from fra.io.video_reader import VideoReader
from fra.profiling.alignment import TemporalAligner
from fra.profiling.reaction_profile_builder import ReactionProfileBuilder
from fra.scoring.comparators import ProfileComparator
from fra.scoring.confidence import ConfidenceEstimator
from fra.scoring.deviation_calculator import DeviationCalculator
from fra.scoring.reaction_interpreter import ReactionInterpreter
from fra.vision.landmark_tracker import FaceLandmarkTracker
from fra.vision.quality_control import FrameQualityAssessor


class ReactionAnalysisPipeline:
    def __init__(self) -> None:
        self.video_reader = VideoReader()
        self.tracker = FaceLandmarkTracker()
        self.quality_assessor = FrameQualityAssessor()
        self.geometric_extractor = GeometricFeatureExtractor()
        self.temporal_extractor = TemporalFeatureExtractor()
        self.normalizer = FeatureNormalizer()
        self.profile_builder = ReactionProfileBuilder()
        self.normative_loader = NormativeProfileLoader()
        self.aligner = TemporalAligner()
        self.comparator = ProfileComparator()
        self.deviation_calculator = DeviationCalculator()
        self.confidence_estimator = ConfidenceEstimator()
        self.reaction_interpreter = ReactionInterpreter()
        self.report_writer = ReportWriter()
        self.stimulus_loader = StimulusDescriptorLoader()

    def run(
        self,
        video_path: str,
        stimulus_description: str,
        normative_profile_path: str,
        output_json_path: str,
        output_csv_path: str | None = None,
    ) -> AnalysisArtifacts:
        stimulus = self.stimulus_loader.load(stimulus_description)
        normative_profile = self.normative_loader.load(normative_profile_path)
        return self.run_with_profile(
            video_path=video_path,
            stimulus=stimulus,
            normative_profile=normative_profile,
            output_json_path=output_json_path,
            output_csv_path=output_csv_path,
            normative_profile_path=normative_profile_path,
        )

    def run_with_profile(
        self,
        video_path: str,
        stimulus: StimulusDescriptor,
        normative_profile: NormativeProfile,
        output_json_path: str,
        output_csv_path: str | None = None,
        normative_profile_path: str | None = None,
    ) -> AnalysisArtifacts:
        frames = self.video_reader.read(video_path)
        processed_frames = []
        feature_vectors = []

        for frame in frames:
            tracked = self.tracker.process(frame)
            assessed = self.quality_assessor.assess(tracked)
            processed_frames.append(assessed)

            if assessed.face_detected and assessed.landmarks is not None:
                feature_vectors.append(self.geometric_extractor.extract(assessed))

        feature_vectors = self.temporal_extractor.enrich(feature_vectors)
        feature_vectors = self.normalizer.normalize(feature_vectors)
        reaction_profile = self.profile_builder.build(stimulus.stimulus_id, feature_vectors)
        reaction_profile.metadata.update(
            {
                "stimulus_category": stimulus.category,
                "stimulus_source_dataset": stimulus.source_dataset or "direct_input",
            }
        )
        if normative_profile_path:
            reaction_profile.metadata["normative_profile_path"] = normative_profile_path
        aligned_actual, aligned_norm = self.aligner.align(reaction_profile, normative_profile)
        comparison = self.comparator.compare(aligned_actual, aligned_norm)
        deviation_result = self.deviation_calculator.calculate(
            comparison,
            thresholds=aligned_norm.thresholds,
        )
        confidence = self.confidence_estimator.estimate(processed_frames, feature_vectors)
        deviation_result.confidence = confidence
        interpretation = self.reaction_interpreter.interpret(
            stimulus=stimulus,
            reaction_profile=aligned_actual,
            normative_profile=aligned_norm,
            deviation_result=deviation_result,
            comparison=comparison,
        )

        self.report_writer.write(
            output_json_path=output_json_path,
            output_csv_path=output_csv_path,
            stimulus=stimulus,
            normative_profile=normative_profile,
            reaction_profile=reaction_profile,
            deviation_result=deviation_result,
            interpretation=interpretation,
            frame_data=processed_frames,
            video_path=video_path,
        )
        return AnalysisArtifacts(
            stimulus=stimulus,
            normative_profile=normative_profile,
            reaction_profile=reaction_profile,
            deviation_result=deviation_result,
            frame_data=processed_frames,
            feature_vectors=feature_vectors,
            comparison=comparison,
            interpretation=interpretation,
        )

    def validate_normative_profile(self, normative_profile_path: str) -> None:
        self.normative_loader.load(normative_profile_path)
        print(f"Normative profile is valid: {normative_profile_path}")

    def export_report(self, input_report_path: str, output_format: str, output_path: str) -> None:
        self.report_writer.export(
            input_report_path=Path(input_report_path),
            output_format=output_format,
            output_path=Path(output_path),
        )
