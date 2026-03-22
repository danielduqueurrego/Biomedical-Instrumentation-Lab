from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from acquisition.arduino_cli_wrapper import UNO_R4_WIFI_BOARD
from acquisition.gui_models import SignalConfiguration


@dataclass(frozen=True, slots=True)
class LabProfile:
    display_name: str
    output_basename: str
    signal_configurations: tuple[SignalConfiguration, ...]
    sketch_dir: Path
    firmware_label: str
    note: str = ""


def _build_signal_configurations(*signal_specs: tuple[str, str, str]) -> tuple[SignalConfiguration, ...]:
    return tuple(
        SignalConfiguration(name=name, preset_name=preset_name, analog_port=analog_port)
        for name, preset_name, analog_port in signal_specs
    )


SHARED_FIRMWARE_LABEL = "UNO R4 WiFi Analog Bank Foundation"
SHARED_FIRMWARE_NOTE = (
    "The current toolbar profiles all use the shared A0-A5 analog capture sketch. "
    "Dedicated lab-specific firmware can replace this later without changing the GUI workflow."
)
PULSE_OX_NOTE = (
    "This profile loads the requested signal labels and the shared analog capture sketch only. "
    "The generated sketch also drives D6 for RED and D5 for IR in the sequence "
    "RED_ON, DARK1, IR_ON, DARK2."
)

LAB_PROFILES = {
    "ECG": LabProfile(
        display_name="ECG",
        output_basename="ecg_lab",
        signal_configurations=_build_signal_configurations(
            ("Raw ECG", "ECG", "A0"),
            ("Amplified ECG", "ECG", "A1"),
            ("Comparator Output", "ECG", "A2"),
        ),
        sketch_dir=UNO_R4_WIFI_BOARD.sketch_dir,
        firmware_label=SHARED_FIRMWARE_LABEL,
        note=SHARED_FIRMWARE_NOTE,
    ),
    "Pulse Oximetry": LabProfile(
        display_name="Pulse Oximetry",
        output_basename="pulse_ox_lab",
        signal_configurations=_build_signal_configurations(
            ("Raw Red Reflective PD Output", "PulseOx", "A0"),
            ("Raw IR Reflective", "PulseOx", "A1"),
            ("Raw Red Transmission", "PulseOx", "A2"),
            ("Raw IR Transmission", "PulseOx", "A3"),
            ("Amplified and Filtered Red Reflective", "PulseOx", "A4"),
            ("Filtered Red Transmission", "PulseOx", "A5"),
        ),
        sketch_dir=UNO_R4_WIFI_BOARD.sketch_dir,
        firmware_label=SHARED_FIRMWARE_LABEL,
        note=PULSE_OX_NOTE,
    ),
    "Blood Pressure": LabProfile(
        display_name="Blood Pressure",
        output_basename="blood_pressure_lab",
        signal_configurations=_build_signal_configurations(
            ("Raw Pressure", "Blood Pressure", "A0"),
            ("Filtered Pressure", "Blood Pressure", "A1"),
            ("Red PD", "Blood Pressure", "A2"),
            ("IR PD", "Blood Pressure", "A3"),
        ),
        sketch_dir=UNO_R4_WIFI_BOARD.sketch_dir,
        firmware_label=SHARED_FIRMWARE_LABEL,
        note=SHARED_FIRMWARE_NOTE,
    ),
    "EMG": LabProfile(
        display_name="EMG",
        output_basename="emg_lab",
        signal_configurations=_build_signal_configurations(
            ("Raw EMG", "EMG", "A0"),
            ("Rectified EMG", "EMG", "A1"),
            ("Enveloped EMG", "EMG", "A2"),
            ("Pressure", "EMG", "A3"),
        ),
        sketch_dir=UNO_R4_WIFI_BOARD.sketch_dir,
        firmware_label=SHARED_FIRMWARE_LABEL,
        note=SHARED_FIRMWARE_NOTE,
    ),
}

LAB_PROFILE_ORDER = ("ECG", "Pulse Oximetry", "Blood Pressure", "EMG")


def get_lab_profile(profile_name: str) -> LabProfile:
    try:
        return LAB_PROFILES[profile_name]
    except KeyError as error:
        available = ", ".join(LAB_PROFILE_ORDER)
        raise KeyError(f"Unknown lab profile {profile_name!r}. Available profiles: {available}") from error
