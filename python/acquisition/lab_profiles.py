from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from acquisition.arduino_cli_wrapper import UNO_R4_WIFI_BOARD
from acquisition.gui_models import SignalConfiguration
from acquisition.lab_manifest import LAB_MANIFEST, LAB_PROFILE_LABELS, get_lab_name_for_profile


@dataclass(frozen=True, slots=True)
class LabProfile:
    display_name: str
    output_basename: str
    signal_configurations: tuple[SignalConfiguration, ...]
    sketch_dir: Path
    firmware_label: str
    note: str = ""


def _build_signal_configurations(*signal_specs) -> tuple[SignalConfiguration, ...]:
    signal_configurations = []
    for name, preset_name, analog_port in signal_specs:
        signal_configurations.append(
            SignalConfiguration(
                name=name,
                preset_name=preset_name,
                analog_port=analog_port,
            )
        )

    return tuple(signal_configurations)


SHARED_FIRMWARE_LABEL = "Generated UNO R4 WiFi Acquisition Firmware"
SHARED_FIRMWARE_NOTE = (
    "The GUI generates UNO R4 WiFi firmware directly from the selected signals and rates."
)
CUSTOM_LAB_PROFILE_NAME = "Custom"
PULSE_OX_NOTE = (
    "This profile runs in PHASED_CYCLE mode. The generated sketch logs raw PHASE packets, "
    "samples all four optical channels on A0 to A3 during every phase, reconstructs corrected "
    "RED and IR cycle outputs, and drives D6 for RED and D5 for IR in the sequence "
    "RED_ON, DARK1, IR_ON, DARK2."
)

PROFILE_SIGNAL_SPECS = {
    "ECG": (
        ("Raw ECG", "ECG", "A0"),
        ("Amplified ECG", "ECG", "A1"),
        ("Comparator Output", "ECG", "A2"),
    ),
    "PulseOx": (
        ("Reflective photodiode raw output", "PulseOx", "A0"),
        ("Transmission photodiode raw output", "PulseOx", "A1"),
        ("Filtered reflective photodiode output", "PulseOx", "A2"),
        ("Filtered transmission photodiode output", "PulseOx", "A3"),
    ),
    "Blood Pressure": (
        ("Raw Pressure", "Blood Pressure", "A0"),
        ("Filtered Pressure", "Blood Pressure", "A1"),
        ("Red PD", "Blood Pressure", "A2"),
        ("IR PD", "Blood Pressure", "A3"),
    ),
    "EMG": (
        ("Raw EMG", "EMG", "A0"),
        ("Rectified EMG", "EMG", "A1"),
        ("Enveloped EMG", "EMG", "A2"),
        ("Pressure", "EMG", "A3"),
    ),
}

PROFILE_OUTPUT_BASENAMES = {
    "ECG": "ecg_lab",
    "PulseOx": "pulse_ox_lab",
    "Blood Pressure": "blood_pressure_lab",
    "EMG": "emg_lab",
}


LAB_PROFILES = {
    manifest_entry.profile_label: LabProfile(
        display_name=manifest_entry.profile_label,
        output_basename=PROFILE_OUTPUT_BASENAMES[manifest_entry.lab_name],
        signal_configurations=_build_signal_configurations(*PROFILE_SIGNAL_SPECS[manifest_entry.lab_name]),
        sketch_dir=UNO_R4_WIFI_BOARD.sketch_dir,
        firmware_label=SHARED_FIRMWARE_LABEL,
        note=PULSE_OX_NOTE if manifest_entry.lab_name == "PulseOx" else SHARED_FIRMWARE_NOTE,
    )
    for manifest_entry in LAB_MANIFEST.values()
}

LAB_PROFILE_ORDER = (CUSTOM_LAB_PROFILE_NAME, *LAB_PROFILE_LABELS)


def get_lab_profile(profile_name: str) -> LabProfile:
    lab_name = get_lab_name_for_profile(profile_name)
    profile_label = LAB_MANIFEST[lab_name].profile_label
    return LAB_PROFILES[profile_label]
