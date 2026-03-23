from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from acquisition.architecture import AcquisitionClass
from acquisition.protocol import PULSEOX_ANALOG_PORTS, UNO_R4_ANALOG_PORTS
from acquisition.presets import LAB_PRESETS


MAX_SIGNAL_COUNT = len(UNO_R4_ANALOG_PORTS)
DEFAULT_ACTIVE_SIGNAL_COUNT = 3
DEFAULT_SIGNAL_PRESETS = tuple(
    preset_name
    for preset_name, preset in LAB_PRESETS.items()
    if preset.acquisition_class != AcquisitionClass.PHASED_CYCLE
)
DEFAULT_GUI_BAUD_RATE = 230400
DEFAULT_BOARD_NAME = "Arduino UNO R4 WiFi"
DEFAULT_BOARD_FQBN = "arduino:renesas_uno:unor4wifi"


@dataclass(frozen=True, slots=True)
class SignalConfiguration:
    name: str
    preset_name: str
    analog_port: str


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
                analog_port=UNO_R4_ANALOG_PORTS[index],
            )
        )
    return tuple(selections)


def default_gui_config(output_dir: Path) -> GuiAcquisitionConfig:
    return GuiAcquisitionConfig(
        board_name=DEFAULT_BOARD_NAME,
        board_fqbn=DEFAULT_BOARD_FQBN,
        port="",
        output_dir=output_dir,
        output_basename="student_session",
        baud_rate=DEFAULT_GUI_BAUD_RATE,
        signal_configurations=default_signal_configurations(),
    )


def validate_signal_configurations(signal_configurations: tuple[SignalConfiguration, ...]) -> None:
    signal_count = len(signal_configurations)
    if not (1 <= signal_count <= MAX_SIGNAL_COUNT):
        raise ValueError(f"Signal count must be between 1 and {MAX_SIGNAL_COUNT}.")

    seen_names = set()
    seen_ports = set()
    for index, signal in enumerate(signal_configurations, start=1):
        normalized_name = signal.name.strip()
        if not normalized_name:
            raise ValueError(f"Signal {index} needs a name.")

        if "," in normalized_name:
            raise ValueError(f"Signal {index} name cannot contain commas because serial metadata uses CSV fields.")

        if normalized_name in seen_names:
            raise ValueError(f"Signal name {normalized_name!r} is used more than once.")
        seen_names.add(normalized_name)

        if signal.preset_name not in LAB_PRESETS:
            raise ValueError(f"Signal {index} uses an unknown preset {signal.preset_name!r}.")

        if signal.analog_port not in UNO_R4_ANALOG_PORTS:
            raise ValueError(f"Signal {index} uses an unsupported analog port {signal.analog_port!r}.")

        if signal.analog_port in seen_ports:
            raise ValueError(f"Analog port {signal.analog_port} is assigned more than once.")
        seen_ports.add(signal.analog_port)

    pulseox_signals = [signal for signal in signal_configurations if signal.preset_name == "PulseOx"]
    if pulseox_signals and len(pulseox_signals) != signal_count:
        raise ValueError("Do not mix PulseOx signals with continuous presets in the same acquisition.")

    if pulseox_signals:
        if signal_count != len(PULSEOX_ANALOG_PORTS):
            raise ValueError(
                f"PulseOx uses {len(PULSEOX_ANALOG_PORTS)} fixed analog channels and must enable exactly that many signals."
            )

        selected_ports = tuple(signal.analog_port for signal in signal_configurations)
        if selected_ports != PULSEOX_ANALOG_PORTS:
            expected_ports = ", ".join(PULSEOX_ANALOG_PORTS)
            raise ValueError(
                "PulseOx uses fixed UNO R4 WiFi wiring and must keep the analog ports in this order: "
                f"{expected_ports}."
            )


def validate_gui_config(config: GuiAcquisitionConfig) -> None:
    if not config.port.strip():
        raise ValueError("Select a serial port before starting acquisition.")

    if not config.output_basename.strip():
        raise ValueError("Enter an output filename before starting acquisition.")

    validate_signal_configurations(config.signal_configurations)
