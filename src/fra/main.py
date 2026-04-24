from fra.cli import build_parser
from fra.api.dataset_analysis import DatasetStimulusAnalyzer
from fra.api.pipeline import ReactionAnalysisPipeline
from fra.api.session import StimulusSessionRunner
from fra.io.stimulus_catalog import DatasetStimulusCatalog


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "analyze":
        pipeline = ReactionAnalysisPipeline()
        pipeline.run(
            video_path=args.video,
            stimulus_description=args.stimulus,
            normative_profile_path=args.norm,
            output_json_path=args.out,
            output_csv_path=args.out_csv,
        )
        return

    if args.command == "run-session":
        session_runner = StimulusSessionRunner()
        session_runner.run(
            dataset=args.dataset,
            stimulus_id=args.stimulus_id,
            category=args.category,
            camera_index=args.camera_index,
            baseline_sec=args.baseline_sec,
            stimulus_sec=args.stimulus_sec,
            recovery_sec=args.recovery_sec,
            captured_video_path=args.captured_video,
            generated_norm_path=args.save_generated_norm,
            headless=args.headless,
            output_json_path=args.out,
            output_csv_path=args.out_csv,
        )
        return

    if args.command == "run-study":
        session_runner = StimulusSessionRunner()
        session_runner.run_study(
            dataset=args.dataset,
            count=args.count,
            category=args.category,
            camera_index=args.camera_index,
            baseline_sec=args.baseline_sec,
            stimulus_sec=args.stimulus_sec,
            recovery_sec=args.recovery_sec,
            artifacts_dir=args.artifacts_dir,
            seed=args.seed,
            headless=args.headless,
            output_json_path=args.out,
            output_csv_path=args.out_csv,
        )
        return

    if args.command == "analyze-dataset-video":
        analyzer = DatasetStimulusAnalyzer()
        analyzer.analyze_video(
            video_path=args.video,
            dataset=args.dataset,
            stimulus_id=args.stimulus_id,
            category=args.category,
            baseline_sec=args.baseline_sec,
            stimulus_sec=args.stimulus_sec,
            recovery_sec=args.recovery_sec,
            generated_norm_path=args.save_generated_norm,
            output_json_path=args.out,
            output_csv_path=args.out_csv,
        )
        return

    if args.command == "validate-profile":
        pipeline = ReactionAnalysisPipeline()
        pipeline.validate_normative_profile(args.norm)
        return

    if args.command == "list-stimuli":
        catalog = DatasetStimulusCatalog()
        entries = catalog.list_entries(
            dataset=args.dataset,
            category=args.category,
            limit=args.limit,
        )
        for entry in entries:
            print(
                f"{entry.stimulus_id}\t{entry.category}\t"
                f"valence={entry.valence_mean:.3f}\tarousal={entry.arousal_mean:.3f}\t"
                f"{entry.description}"
            )
        return

    if args.command == "export-report":
        pipeline = ReactionAnalysisPipeline()
        pipeline.export_report(
            input_report_path=args.input,
            output_format=args.format,
            output_path=args.out,
        )
