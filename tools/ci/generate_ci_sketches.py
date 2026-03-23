#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_DIR = REPO_ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from acquisition.arduino_codegen import create_generated_analog_capture_sketch
from acquisition.lab_profiles import get_lab_profile


CI_GENERATED_EXAMPLES = (
    ("generated_cont_med_sketch_dir", "ECG"),
    ("generated_cont_high_sketch_dir", "EMG"),
    ("generated_phased_cycle_sketch_dir", "Pulse Oximetry"),
)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate one CI smoke-test sketch for each supported acquisition class.",
    )
    parser.add_argument(
        "--github-output",
        default=None,
        help="Optional path to the GitHub Actions output file.",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()

    generated_outputs: list[tuple[str, str]] = []
    for output_name, profile_name in CI_GENERATED_EXAMPLES:
        profile = get_lab_profile(profile_name)
        artifact = create_generated_analog_capture_sketch(profile.signal_configurations, baud_rate=230400)
        generated_outputs.append((output_name, str(artifact.sketch_dir)))
        print(
            f"{profile_name}: {artifact.acquisition_class} "
            f"at {artifact.sample_rate_hz} Hz -> {artifact.sketch_dir}"
        )

    if args.github_output:
        output_path = Path(args.github_output)
        with output_path.open("a", encoding="utf-8") as handle:
            for output_name, output_value in generated_outputs:
                handle.write(f"{output_name}={output_value}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
