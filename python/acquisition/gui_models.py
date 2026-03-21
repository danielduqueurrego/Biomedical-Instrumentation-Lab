from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from acquisition.arduino_cli_wrapper import UNO_R4_WIFI_BOARD
from acquisition.presets import LAB_PRESETS


MAX_SIGNAL_COUNT = 3
DEFAULT_SIGNAL_PRESETS = ("EMG", "ECG", "Blood Pressure")
DEFAULT_GUI_BAUD_RATE = 230400


@dataclass(frozen=True, slots=True)
class SignalConfiguration:
    name: str
    preset_name: str


@dataclass(frozen=True, slots=True)
class GuiAcquisitionConfig:
    board_name: str
    board_fqbn: str
    port: str
    output_dir: Path
    output_basename: str
    baud_rate: int
    signal_configurations: tuple[SignalConfiguration, ...]

    @property
    def signal_count(self) -> int:
        return len(self.signal_configurations)


def default_signal_configurations(count: int = MAX_SIGNAL_COUNT) -> tuple[SignalConfiguration, ...]:
    selections = []
    for index in range(count):
        preset_name = DEFAULT_SIGNAL_PRESETS[index % len(DEFAULT_SIGNAL_PRESETS)]
        selections.append(
            SignalConfiguration(
                name=f"Signal {index + 1}",
                preset_name=preset_name,
            )
        )
    return tuple(selections)


def default_gui_config(output_dir: Path) -> GuiAcquisitionConfig:
    return GuiAcquisitionConfig(
        board_name=UNO_R4_WIFI_BOARD.display_name,
        board_fqbn=UNO_R4_WIFI_BOARD.fqbn,
        port="",
        output_dir=output_dir,
        output_basename="student_session",
        baud_rate=DEFAULT_GUI_BAUD_RATE,
        signal_configurations=default_signal_configurations(),
    )


def validate_gui_config(config: GuiAcquisitionConfig) -> None:
    if not config.port.strip():
        raise ValueError("Select a serial port before starting acquisition.")

    if not config.output_basename.strip():
        raise ValueError("Enter an output filename before starting acquisition.")

    if not (1 <= config.signal_count <= MAX_SIGNAL_COUNT):
        raise ValueError(f"Signal count must be between 1 and {MAX_SIGNAL_COUNT}.")

    seen_names = set()
    for index, signal in enumerate(config.signal_configurations, start=1):
        normalized_name = signal.name.strip()
        if not normalized_name:
            raise ValueError(f"Signal {index} needs a name.")

        if normalized_name in seen_names:
            raise ValueError(f"Signal name {normalized_name!r} is used more than once.")
        seen_names.add(normalized_name)

        if signal.preset_name not in LAB_PRESETS:
            raise ValueError(f"Signal {index} uses an unknown preset {signal.preset_name!r}.")
