from dataclasses import dataclass

from acquisition.architecture import AcquisitionClass, PlotDefaults
from acquisition.lab_manifest import LAB_MANIFEST


CONT_HIGH_CLASSIFICATION_RATE_HZ = 500


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


# This preset table is the canonical lab manifest for default rates, packet types,
# and default field layouts used elsewhere in the repo.
LAB_PRESETS = {
    lab_name: SamplingPreset(
        lab_name=entry.lab_name,
        acquisition_class=entry.acquisition_class,
        default_sample_rate_hz=entry.default_sample_rate_hz,
        default_cycle_rate_hz=entry.default_cycle_rate_hz,
        packet_types=entry.packet_types,
        default_fields=entry.default_fields,
        plotting=entry.plotting,
        phase_names=entry.phase_names,
        notes=entry.notes,
    )
    for lab_name, entry in LAB_MANIFEST.items()
}


def get_preset(lab_name: str) -> SamplingPreset:
    try:
        return LAB_PRESETS[lab_name]
    except KeyError as error:
        available = ", ".join(sorted(LAB_PRESETS))
        raise KeyError(f"Unknown lab preset {lab_name!r}. Available presets: {available}") from error


def is_phased_cycle_preset(preset_name: str) -> bool:
    return get_preset(preset_name).acquisition_class == AcquisitionClass.PHASED_CYCLE


def default_sample_rate_hz_for_signal_configurations(signal_configurations) -> int:
    rates = []
    for signal_configuration in signal_configurations:
        preset = get_preset(signal_configuration.preset_name)
        rate_hz = preset.default_sample_rate_hz or preset.default_cycle_rate_hz
        if rate_hz is not None:
            rates.append(rate_hz)
    return max(rates, default=0)


def continuous_acquisition_class_name_for_rate_hz(sample_rate_hz: int) -> str:
    return "CONT_HIGH" if sample_rate_hz > CONT_HIGH_CLASSIFICATION_RATE_HZ else "CONT_MED"


def continuous_timestamp_field_name_for_rate_hz(sample_rate_hz: int) -> str:
    return "t_us" if continuous_acquisition_class_name_for_rate_hz(sample_rate_hz) == "CONT_HIGH" else "t_ms"
