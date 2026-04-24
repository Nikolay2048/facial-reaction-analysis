from __future__ import annotations

import argparse

from pydantic import BaseModel


class CLIConfig(BaseModel):
    command: str
    video: str | None = None
    stimulus: str | None = None
    norm: str | None = None
    out: str | None = None
    out_csv: str | None = None
    input: str | None = None
    format: str | None = None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fra",
        description="Computer vision pipeline for facial reaction deviation analysis.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Run reaction analysis on a video.")
    analyze.add_argument("--video", required=True, help="Path to the reaction video.")
    analyze.add_argument(
        "--stimulus",
        required=True,
        help="Visual stimulus description used for selecting and interpreting the reaction profile.",
    )
    analyze.add_argument("--norm", required=True, help="Path to the normative profile JSON.")
    analyze.add_argument("--out", required=True, help="Path to the JSON report output.")
    analyze.add_argument("--out-csv", required=False, help="Optional path to the CSV timeline.")

    dataset_analyze = subparsers.add_parser(
        "analyze-dataset-video",
        help="Analyze a prerecorded reaction video against a stimulus selected from OASIS or GAPED.",
    )
    dataset_analyze.add_argument("--video", required=True, help="Path to the prerecorded reaction video.")
    dataset_analyze.add_argument("--dataset", choices=["oasis", "gaped", "artemis"], required=True)
    dataset_analyze.add_argument("--stimulus-id", required=False, help="Optional dataset-specific stimulus ID.")
    dataset_analyze.add_argument("--category", required=False, help="Optional stimulus category filter.")
    dataset_analyze.add_argument("--baseline-sec", type=float, default=1.0)
    dataset_analyze.add_argument("--stimulus-sec", type=float, default=3.0)
    dataset_analyze.add_argument("--recovery-sec", type=float, default=2.0)
    dataset_analyze.add_argument(
        "--save-generated-norm",
        required=False,
        help="Optional path to save the generated normative profile JSON.",
    )
    dataset_analyze.add_argument("--out", required=True, help="Path to the JSON report output.")
    dataset_analyze.add_argument("--out-csv", required=False, help="Optional path to the CSV timeline.")

    session = subparsers.add_parser(
        "run-session",
        help="Display a dataset image stimulus, record webcam reaction, and analyze deviation.",
    )
    session.add_argument("--dataset", choices=["oasis", "gaped", "artemis"], required=True)
    session.add_argument("--stimulus-id", required=False, help="Optional dataset-specific stimulus ID.")
    session.add_argument("--category", required=False, help="Optional stimulus category filter.")
    session.add_argument("--camera-index", type=int, default=0)
    session.add_argument("--baseline-sec", type=float, default=1.0)
    session.add_argument("--stimulus-sec", type=float, default=3.0)
    session.add_argument("--recovery-sec", type=float, default=2.0)
    session.add_argument("--captured-video", required=False, help="Optional path to save recorded reaction video.")
    session.add_argument(
        "--save-generated-norm",
        required=False,
        help="Optional path to save the generated normative profile JSON.",
    )
    session.add_argument("--headless", action="store_true", help="Disable stimulus display window.")
    session.add_argument("--out", required=True, help="Path to the JSON report output.")
    session.add_argument("--out-csv", required=False, help="Optional path to the CSV timeline.")

    study = subparsers.add_parser(
        "run-study",
        help="Run a multi-stimulus webcam session and build a final summary report.",
    )
    study.add_argument("--dataset", choices=["oasis", "gaped", "artemis"], required=True)
    study.add_argument("--count", type=int, required=True, help="Number of stimuli to show in the session.")
    study.add_argument("--category", required=False, help="Optional stimulus category filter.")
    study.add_argument("--camera-index", type=int, default=0)
    study.add_argument("--baseline-sec", type=float, default=1.0)
    study.add_argument("--stimulus-sec", type=float, default=3.0)
    study.add_argument("--recovery-sec", type=float, default=2.0)
    study.add_argument("--headless", action="store_true", help="Disable stimulus display window.")
    study.add_argument("--seed", type=int, required=False, help="Optional random seed for stimulus sampling.")
    study.add_argument("--out", required=True, help="Path to the final JSON study report output.")
    study.add_argument("--out-csv", required=False, help="Optional path to the final CSV study summary.")
    study.add_argument(
        "--artifacts-dir",
        required=False,
        help="Optional directory for per-stimulus videos, generated norms, JSON reports, and CSV timelines.",
    )

    validate = subparsers.add_parser(
        "validate-profile",
        help="Validate normative profile structure.",
    )
    validate.add_argument("--norm", required=True, help="Path to the normative profile JSON.")

    list_stimuli = subparsers.add_parser(
        "list-stimuli",
        help="List available stimuli from supported local datasets.",
    )
    list_stimuli.add_argument("--dataset", choices=["oasis", "gaped", "artemis"], required=True)
    list_stimuli.add_argument("--category", required=False, help="Optional category filter.")
    list_stimuli.add_argument("--limit", type=int, default=20)

    export = subparsers.add_parser(
        "export-report",
        help="Convert an existing report to JSON or CSV.",
    )
    export.add_argument("--input", required=True, help="Path to an existing JSON report.")
    export.add_argument("--format", choices=["json", "csv"], required=True)
    export.add_argument("--out", required=True, help="Export destination path.")

    return parser
