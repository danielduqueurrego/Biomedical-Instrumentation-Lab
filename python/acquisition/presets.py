from dataclasses import dataclass

from acquisition.architecture import AcquisitionClass, PlotDefaults


@dataclass(frozen=True, slots=True)
class SamplingPreset:
    lab_name: str
    acquisition_class: AcquisitionClass
    default_sample_rate_hz: int | None
    default_cycle_rate_hz: int | None
    packet_types: tuple[str, ...]
    default_fields: tuple[str, ...]
    plotting: PlotDefaults
    phase_names: tuple[str, ...] = ()
    notes: str = ""


LAB_PRESETS = {
    "EMG": SamplingPreset(
        lab_name="EMG",
        acquisition_class=AcquisitionClass.CONT_HIGH,
        default_sample_rate_hz=2000,
        default_cycle_rate_hz=None,
        packet_types=("META", "DATA", "STAT", "ERR"),
        default_fields=("t_ms", "ch1"),
        plotting=PlotDefaults(history_seconds=5.0, update_interval_ms=50),
        notes="High-rate waveform starter preset for student EMG labs.",
    ),
    "ECG": SamplingPreset(
        lab_name="ECG",
        acquisition_class=AcquisitionClass.CONT_MED,
        default_sample_rate_hz=500,
        default_cycle_rate_hz=None,
        packet_types=("META", "DATA", "STAT", "ERR"),
        default_fields=("t_ms", "ch1"),
        plotting=PlotDefaults(history_seconds=10.0, update_interval_ms=100),
        notes="Medium-rate waveform starter preset for student ECG labs.",
    ),
    "PulseOx": SamplingPreset(
        lab_name="PulseOx",
        acquisition_class=AcquisitionClass.PHASED_CYCLE,
        default_sample_rate_hz=None,
        default_cycle_rate_hz=100,
        packet_types=("META", "PHASE", "CYCLE", "STAT", "ERR"),
        default_fields=("t_us", "cycle_idx", "red_corr", "ir_corr"),
        plotting=PlotDefaults(history_seconds=15.0, update_interval_ms=100),
        phase_names=("RED_ON", "DARK1", "IR_ON", "DARK2"),
        notes="Cycle rate is a software default for the pulse-ox teaching workflow.",
    ),
    "Blood Pressure": SamplingPreset(
        lab_name="Blood Pressure",
        acquisition_class=AcquisitionClass.CONT_MED,
        default_sample_rate_hz=200,
        default_cycle_rate_hz=None,
        packet_types=("META", "DATA", "STAT", "ERR"),
        default_fields=("t_ms", "pressure"),
        plotting=PlotDefaults(history_seconds=20.0, update_interval_ms=200),
        notes="Blood pressure is treated as a continuous waveform lab with manual cuff control.",
    ),
}


def get_preset(lab_name: str) -> SamplingPreset:
    try:
        return LAB_PRESETS[lab_name]
    except KeyError as error:
        available = ", ".join(sorted(LAB_PRESETS))
        raise KeyError(f"Unknown lab preset {lab_name!r}. Available presets: {available}") from error
