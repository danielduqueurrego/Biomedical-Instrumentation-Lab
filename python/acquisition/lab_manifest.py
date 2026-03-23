from __future__ import annotations

from dataclasses import dataclass

from acquisition.architecture import AcquisitionClass, PlotDefaults


@dataclass(frozen=True, slots=True)
class LabManifestEntry:
    """Canonical per-lab acquisition metadata used by presets and GUI profiles."""

    lab_name: str
    profile_label: str
    acquisition_class: AcquisitionClass
    default_sample_rate_hz: int | None
    default_cycle_rate_hz: int | None
    packet_types: tuple[str, ...]
    default_fields: tuple[str, ...]
    plotting: PlotDefaults
    phase_names: tuple[str, ...] = ()
    notes: str = ""


LAB_MANIFEST = {
    "EMG": LabManifestEntry(
        lab_name="EMG",
        profile_label="EMG",
        acquisition_class=AcquisitionClass.CONT_HIGH,
        default_sample_rate_hz=2000,
        default_cycle_rate_hz=None,
        packet_types=("META", "DATA", "STAT", "ERR"),
        default_fields=("t_ms", "ch1"),
        plotting=PlotDefaults(history_seconds=5.0, update_interval_ms=50),
        notes="High-rate waveform starter preset for student EMG labs.",
    ),
    "ECG": LabManifestEntry(
        lab_name="ECG",
        profile_label="ECG",
        acquisition_class=AcquisitionClass.CONT_MED,
        default_sample_rate_hz=500,
        default_cycle_rate_hz=None,
        packet_types=("META", "DATA", "STAT", "ERR"),
        default_fields=("t_ms", "ch1"),
        plotting=PlotDefaults(history_seconds=10.0, update_interval_ms=100),
        notes="Medium-rate waveform starter preset for student ECG labs.",
    ),
    "PulseOx": LabManifestEntry(
        lab_name="PulseOx",
        profile_label="Pulse Oximetry",
        acquisition_class=AcquisitionClass.PHASED_CYCLE,
        default_sample_rate_hz=None,
        default_cycle_rate_hz=100,
        packet_types=("META", "PHASE", "CYCLE", "STAT", "ERR"),
        default_fields=("t_us", "cycle_idx", "red_corr", "ir_corr"),
        plotting=PlotDefaults(history_seconds=15.0, update_interval_ms=100),
        phase_names=("RED_ON", "DARK1", "IR_ON", "DARK2"),
        notes="Cycle rate is a software default for the pulse-ox teaching workflow.",
    ),
    "Blood Pressure": LabManifestEntry(
        lab_name="Blood Pressure",
        profile_label="Blood Pressure",
        acquisition_class=AcquisitionClass.CONT_MED,
        default_sample_rate_hz=200,
        default_cycle_rate_hz=None,
        packet_types=("META", "DATA", "STAT", "ERR"),
        default_fields=("t_ms", "pressure"),
        plotting=PlotDefaults(history_seconds=20.0, update_interval_ms=200),
        notes="Blood pressure is treated as a continuous waveform lab with manual cuff control.",
    ),
}

LAB_PROFILE_LABELS = tuple(entry.profile_label for entry in LAB_MANIFEST.values())
LAB_PROFILE_TO_PRESET = {entry.profile_label: entry.lab_name for entry in LAB_MANIFEST.values()}


def get_manifest_entry(lab_name: str) -> LabManifestEntry:
    try:
        return LAB_MANIFEST[lab_name]
    except KeyError as error:
        available = ", ".join(sorted(LAB_MANIFEST))
        raise KeyError(f"Unknown lab manifest entry {lab_name!r}. Available labs: {available}") from error


def get_lab_name_for_profile(profile_label: str) -> str:
    try:
        return LAB_PROFILE_TO_PRESET[profile_label]
    except KeyError as error:
        available = ", ".join(LAB_PROFILE_LABELS)
        raise KeyError(f"Unknown lab profile {profile_label!r}. Available profiles: {available}") from error
