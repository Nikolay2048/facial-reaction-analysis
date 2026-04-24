from fra.cli import build_parser


def test_build_parser_analyze_command() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "analyze",
            "--video",
            "sample.mp4",
            "--stimulus",
            "test stimulus",
            "--norm",
            "norm.json",
            "--out",
            "report.json",
        ]
    )
    assert args.command == "analyze"
    assert args.video == "sample.mp4"


def test_build_parser_run_session_command() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "run-session",
            "--dataset",
            "artemis",
            "--stimulus-id",
            "vincent-van-gogh_portrait-of-madame-ginoux-l-arlesienne-1890",
            "--save-generated-norm",
            "norm.json",
            "--out",
            "report.json",
        ]
    )
    assert args.command == "run-session"
    assert args.dataset == "artemis"
    assert args.stimulus_id == "vincent-van-gogh_portrait-of-madame-ginoux-l-arlesienne-1890"
    assert args.save_generated_norm == "norm.json"


def test_build_parser_analyze_dataset_video_command() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "analyze-dataset-video",
            "--video",
            "sample.mp4",
            "--dataset",
            "gaped",
            "--stimulus-id",
            "P001",
            "--save-generated-norm",
            "generated_norm.json",
            "--out",
            "report.json",
        ]
    )
    assert args.command == "analyze-dataset-video"
    assert args.dataset == "gaped"
    assert args.video == "sample.mp4"
    assert args.save_generated_norm == "generated_norm.json"


def test_build_parser_list_stimuli_command() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "list-stimuli",
            "--dataset",
            "oasis",
            "--limit",
            "5",
        ]
    )
    assert args.command == "list-stimuli"
    assert args.limit == 5


def test_build_parser_run_study_command() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "run-study",
            "--dataset",
            "oasis",
            "--count",
            "3",
            "--out",
            "study.json",
            "--out-csv",
            "study.csv",
        ]
    )
    assert args.command == "run-study"
    assert args.dataset == "oasis"
    assert args.count == 3
