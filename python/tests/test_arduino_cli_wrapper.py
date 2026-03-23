"""Regression tests for Arduino CLI board matching and upload routing."""

from __future__ import annotations

import sys
from pathlib import Path

from acquisition import arduino_cli_wrapper
from acquisition.arduino_cli_wrapper import (
    ArduinoCli,
    BoardDefinition,
    CONT_HIGH_UNO_R4_EMG_SKETCH_DIR,
    DetectedBoardPort,
    UNO_R4_WIFI_BOARD,
)


def test_detect_port_for_board_matches_same_hardware_identity_not_object_identity() -> None:
    cli = ArduinoCli("arduino-cli")
    duplicate_board_identity = BoardDefinition(
        display_name=UNO_R4_WIFI_BOARD.display_name,
        fqbn=UNO_R4_WIFI_BOARD.fqbn,
        core=UNO_R4_WIFI_BOARD.core,
    )
    cli.list_supported_board_ports = lambda: [  # type: ignore[method-assign]
        DetectedBoardPort(
            port="COM11",
            board_name=duplicate_board_identity.display_name,
            fqbn=duplicate_board_identity.fqbn,
            description="Arduino UNO R4 WiFi on COM11",
            matched_board=duplicate_board_identity,
        )
    ]

    detected_port = cli.detect_port_for_board(UNO_R4_WIFI_BOARD)

    assert detected_port == "COM11"


def test_upload_cont_high_emg_uses_shared_board_detection_without_port(monkeypatch) -> None:
    class FakeCli:
        def __init__(self) -> None:
            self.detect_calls = []
            self.upload_calls = []

        def detect_port_for_board(self, board):
            self.detect_calls.append(board)
            return "COM7"

        def upload(self, sketch_dir: Path, fqbn: str, port: str, verbose: bool = False) -> None:
            self.upload_calls.append((sketch_dir, fqbn, port, verbose))

    fake_cli = FakeCli()
    monkeypatch.setattr(ArduinoCli, "from_environment", classmethod(lambda cls, _: fake_cli))
    monkeypatch.setattr(sys, "argv", ["arduino_cli_wrapper.py", "upload-cont-high-emg", "--skip-compile"])

    result = arduino_cli_wrapper.main()

    assert result == 0
    assert fake_cli.detect_calls == [UNO_R4_WIFI_BOARD]
    assert fake_cli.upload_calls == [
        (CONT_HIGH_UNO_R4_EMG_SKETCH_DIR, UNO_R4_WIFI_BOARD.fqbn, "COM7", False)
    ]
