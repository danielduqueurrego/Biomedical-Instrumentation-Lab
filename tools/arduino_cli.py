#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_SKETCH_DIR = REPO_ROOT / "firmware" / "cont_med" / "uno_r4_wifi" / "three_channel_data_demo"
DEFAULT_CORE = "arduino:renesas_uno"
DEFAULT_FQBN = "arduino:renesas_uno:unor4wifi"
BOARD_NAME = "Arduino UNO R4 WiFi"


def resolve_arduino_cli(explicit_path: str | None) -> str:
    candidate_paths = []

    if explicit_path:
        candidate_paths.append(Path(explicit_path))

    env_path = os.environ.get("ARDUINO_CLI")
    if env_path:
        candidate_paths.append(Path(env_path))

    for candidate in candidate_paths:
        if candidate.is_file():
            return str(candidate)

    discovered_path = shutil.which("arduino-cli")
    if discovered_path:
        return discovered_path

    raise FileNotFoundError(
        "Arduino CLI was not found. Add it to PATH, set ARDUINO_CLI, or pass --arduino-cli /path/to/arduino-cli."
    )


def run_arduino_cli(cli_path: str, command: list[str], capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [cli_path, *command],
        check=True,
        text=True,
        capture_output=capture_output,
    )


def detect_uno_r4_port(cli_path: str) -> str:
    result = run_arduino_cli(cli_path, ["board", "list"], capture_output=True)
    matches = []

    for line in result.stdout.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("Port"):
            continue

        if BOARD_NAME in stripped or DEFAULT_FQBN in stripped:
            matches.append(stripped.split()[0])

    if not matches:
        raise RuntimeError(
            "Could not auto-detect an Arduino UNO R4 WiFi port. Connect the board and try again, "
            "or re-run with --port."
        )

    unique_matches = sorted(set(matches))
    if len(unique_matches) > 1:
        joined = ", ".join(unique_matches)
        raise RuntimeError(f"Multiple possible UNO R4 WiFi ports were found: {joined}. Re-run with --port.")

    return unique_matches[0]


def setup_board(cli_path: str) -> None:
    print("Updating Arduino core index...")
    run_arduino_cli(cli_path, ["core", "update-index"])
    print(f"Installing board core {DEFAULT_CORE}...")
    run_arduino_cli(cli_path, ["core", "install", DEFAULT_CORE])
    print("Arduino CLI setup finished.")


def compile_demo(cli_path: str, verbose: bool) -> None:
    command = ["compile", "--fqbn", DEFAULT_FQBN]
    if verbose:
        command.append("--verbose")
    command.append(str(DEMO_SKETCH_DIR))

    print(f"Compiling {DEMO_SKETCH_DIR.name} for {DEFAULT_FQBN}...")
    run_arduino_cli(cli_path, command)
    print("Compile finished.")


def upload_demo(cli_path: str, port: str | None, verbose: bool, skip_compile: bool) -> None:
    selected_port = port or detect_uno_r4_port(cli_path)

    if not skip_compile:
        compile_demo(cli_path, verbose=verbose)

    command = ["upload", "--fqbn", DEFAULT_FQBN, "--port", selected_port]
    if verbose:
        command.append("--verbose")
    command.append(str(DEMO_SKETCH_DIR))

    print(f"Uploading {DEMO_SKETCH_DIR.name} to {selected_port}...")
    run_arduino_cli(cli_path, command)
    print("Upload finished.")


def board_list(cli_path: str) -> None:
    run_arduino_cli(cli_path, ["board", "list"])


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cross-platform helper for the Arduino CLI workflow used in Biomedical-Instrumentation-Lab.",
    )
    parser.add_argument(
        "--arduino-cli",
        default=None,
        help="Full path to the Arduino CLI executable. Optional if arduino-cli is already on PATH.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("setup", help="Install or update the Arduino UNO R4 WiFi board core.")
    subparsers.add_parser("board-list", help="Show the serial boards detected by Arduino CLI.")

    compile_parser = subparsers.add_parser("compile-demo", help="Compile the CONT_MED three-channel reference sketch.")
    compile_parser.add_argument("--verbose", action="store_true", help="Show verbose Arduino CLI output.")

    upload_parser = subparsers.add_parser("upload-demo", help="Compile and upload the CONT_MED three-channel sketch.")
    upload_parser.add_argument("--port", default=None, help="Serial port such as COM3 or /dev/ttyACM0.")
    upload_parser.add_argument("--skip-compile", action="store_true", help="Upload without compiling first.")
    upload_parser.add_argument("--verbose", action="store_true", help="Show verbose Arduino CLI output.")

    return parser


def main() -> int:
    args = build_arg_parser().parse_args()

    try:
        cli_path = resolve_arduino_cli(args.arduino_cli)
    except FileNotFoundError as error:
        print(error, file=sys.stderr)
        return 2

    try:
        if args.command == "setup":
            setup_board(cli_path)
        elif args.command == "board-list":
            board_list(cli_path)
        elif args.command == "compile-demo":
            compile_demo(cli_path, verbose=args.verbose)
        elif args.command == "upload-demo":
            upload_demo(cli_path, port=args.port, verbose=args.verbose, skip_compile=args.skip_compile)
        else:
            raise RuntimeError(f"Unsupported command: {args.command}")
    except subprocess.CalledProcessError as error:
        return error.returncode or 1
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
