from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class ArduinoCliError(RuntimeError):
    """Raised when Arduino CLI could not complete the requested operation."""


@dataclass(frozen=True, slots=True)
class BoardDefinition:
    display_name: str
    fqbn: str
    core: str
    sketch_dir: Path


@dataclass(frozen=True, slots=True)
class BoardPort:
    port: str
    description: str


@dataclass(frozen=True, slots=True)
class DetectedBoardPort:
    port: str
    board_name: str
    fqbn: str
    description: str
    matched_board: BoardDefinition | None = None


UNO_R4_WIFI_BOARD = BoardDefinition(
    display_name="Arduino UNO R4 WiFi",
    fqbn="arduino:renesas_uno:unor4wifi",
    core="arduino:renesas_uno",
    sketch_dir=REPO_ROOT / "firmware" / "cont_med" / "uno_r4_wifi" / "three_channel_data_demo",
)

SUPPORTED_BOARDS = (UNO_R4_WIFI_BOARD,)
FQBN_PATTERN = re.compile(r"[A-Za-z0-9_.-]+:[A-Za-z0-9_.-]+:[A-Za-z0-9_.-]+")


def resolve_arduino_cli(explicit_path: str | None = None) -> str:
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


class ArduinoCli:
    def __init__(self, executable_path: str):
        self.executable_path = executable_path

    @classmethod
    def from_environment(cls, explicit_path: str | None = None) -> "ArduinoCli":
        return cls(resolve_arduino_cli(explicit_path))

    def run(self, args: list[str], capture_output: bool = False) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                [self.executable_path, *args],
                check=True,
                text=True,
                capture_output=capture_output,
            )
        except subprocess.CalledProcessError as error:
            stderr = error.stderr.strip() if error.stderr else ""
            stdout = error.stdout.strip() if error.stdout else ""
            details = stderr or stdout or f"Process exited with code {error.returncode}."
            raise ArduinoCliError(details) from error

    def version(self) -> str:
        result = self.run(["version"], capture_output=True)
        return result.stdout.strip()

    def _match_supported_board(self, board_name: str, fqbn: str, description: str) -> BoardDefinition | None:
        normalized_name = board_name.lower()
        normalized_description = description.lower()

        for board in SUPPORTED_BOARDS:
            if fqbn == board.fqbn:
                return board

            display_name = board.display_name.lower()
            if display_name in normalized_name or display_name in normalized_description:
                return board

        return None

    def _parse_board_list_line(self, line: str) -> DetectedBoardPort | None:
        stripped = line.strip()
        if not stripped or stripped.startswith("Port"):
            return None

        parts = [part.strip() for part in re.split(r"\s{2,}", stripped) if part.strip()]
        if not parts:
            return None

        port = parts[0].split()[0]
        fqbn = ""
        fqbn_index = None

        for index, part in enumerate(parts):
            if FQBN_PATTERN.fullmatch(part):
                fqbn = part
                fqbn_index = index
                break

        board_name = ""
        if fqbn_index is not None and fqbn_index > 0:
            board_name = parts[fqbn_index - 1]

        matched_board = self._match_supported_board(board_name, fqbn, stripped)
        if matched_board is not None and not board_name:
            board_name = matched_board.display_name

        if not board_name:
            board_name = "Unknown board"

        return DetectedBoardPort(
            port=port,
            board_name=board_name,
            fqbn=fqbn,
            description=stripped,
            matched_board=matched_board,
        )

    def list_board_ports(self) -> list[BoardPort]:
        return [
            BoardPort(port=detected.port, description=detected.description)
            for detected in self.list_detected_boards()
        ]

    def list_detected_boards(self) -> list[DetectedBoardPort]:
        result = self.run(["board", "list"], capture_output=True)
        detected_boards = []

        for line in result.stdout.splitlines():
            parsed = self._parse_board_list_line(line)
            if parsed is not None:
                detected_boards.append(parsed)

        return detected_boards

    def list_supported_board_ports(self) -> list[DetectedBoardPort]:
        return [detected for detected in self.list_detected_boards() if detected.matched_board is not None]

    def detect_port_for_board(self, board: BoardDefinition) -> str:
        matches = []

        for detected in self.list_supported_board_ports():
            if detected.matched_board == board:
                matches.append(detected.port)

        unique_matches = sorted(set(matches))
        if not unique_matches:
            raise ArduinoCliError(
                f"Could not auto-detect a port for {board.display_name}. Connect the board and try again, or select a port manually."
            )

        if len(unique_matches) > 1:
            joined = ", ".join(unique_matches)
            raise ArduinoCliError(
                f"Multiple possible ports were found for {board.display_name}: {joined}. Select one manually."
            )

        return unique_matches[0]

    def update_index(self) -> None:
        self.run(["core", "update-index"])

    def install_core(self, core: str) -> None:
        self.run(["core", "install", core])

    def compile(self, sketch_dir: Path, fqbn: str, verbose: bool = False) -> None:
        args = ["compile", "--fqbn", fqbn]
        if verbose:
            args.append("--verbose")
        args.append(str(sketch_dir))
        self.run(args)

    def upload(self, sketch_dir: Path, fqbn: str, port: str, verbose: bool = False) -> None:
        args = ["upload", "--fqbn", fqbn, "--port", port]
        if verbose:
            args.append("--verbose")
        args.append(str(sketch_dir))
        self.run(args)


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
        cli = ArduinoCli.from_environment(args.arduino_cli)
    except FileNotFoundError as error:
        print(error, file=sys.stderr)
        return 2

    try:
        if args.command == "setup":
            print("Updating Arduino core index...")
            cli.update_index()
            print(f"Installing board core {UNO_R4_WIFI_BOARD.core}...")
            cli.install_core(UNO_R4_WIFI_BOARD.core)
            print("Arduino CLI setup finished.")
        elif args.command == "board-list":
            for board_port in cli.list_board_ports():
                print(board_port.description)
        elif args.command == "compile-demo":
            print(f"Compiling {UNO_R4_WIFI_BOARD.sketch_dir.name} for {UNO_R4_WIFI_BOARD.fqbn}...")
            cli.compile(UNO_R4_WIFI_BOARD.sketch_dir, UNO_R4_WIFI_BOARD.fqbn, verbose=args.verbose)
            print("Compile finished.")
        elif args.command == "upload-demo":
            if not args.skip_compile:
                print(f"Compiling {UNO_R4_WIFI_BOARD.sketch_dir.name} for {UNO_R4_WIFI_BOARD.fqbn}...")
                cli.compile(UNO_R4_WIFI_BOARD.sketch_dir, UNO_R4_WIFI_BOARD.fqbn, verbose=args.verbose)
                print("Compile finished.")

            selected_port = args.port or cli.detect_port_for_board(UNO_R4_WIFI_BOARD)
            print(f"Uploading {UNO_R4_WIFI_BOARD.sketch_dir.name} to {selected_port}...")
            cli.upload(UNO_R4_WIFI_BOARD.sketch_dir, UNO_R4_WIFI_BOARD.fqbn, selected_port, verbose=args.verbose)
            print("Upload finished.")
        else:
            raise ArduinoCliError(f"Unsupported command: {args.command}")
    except ArduinoCliError as error:
        print(error, file=sys.stderr)
        return 1

    return 0
