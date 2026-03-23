from dataclasses import dataclass

from acquisition.architecture import AcquisitionClass, PlotDefaults
from acquisition.lab_manifest import LAB_MANIFEST


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
