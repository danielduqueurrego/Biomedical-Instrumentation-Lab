from dataclasses import dataclass
from enum import StrEnum


class AcquisitionClass(StrEnum):
    CONT_HIGH = "CONT_HIGH"
    CONT_MED = "CONT_MED"
    PHASED_CYCLE = "PHASED_CYCLE"


@dataclass(frozen=True, slots=True)
class PlotDefaults:
    history_seconds: float
    update_interval_ms: int


@dataclass(frozen=True, slots=True)
class PatternDefinition:
    acquisition_class: AcquisitionClass
    summary: str
    primary_packets: tuple[str, ...]
    rate_guidance: str
    plotting_guidance: str


PATTERN_DEFINITIONS = {
    AcquisitionClass.CONT_HIGH: PatternDefinition(
        acquisition_class=AcquisitionClass.CONT_HIGH,
        summary="High-rate continuous waveform acquisition.",
        primary_packets=("META", "DATA", "STAT", "ERR"),
        rate_guidance="Use when the lab needs about 1000 samples/s or more.",
        plotting_guidance="Log every sample and redraw the plot less often than the sample rate.",
    ),
    AcquisitionClass.CONT_MED: PatternDefinition(
        acquisition_class=AcquisitionClass.CONT_MED,
        summary="Medium-rate continuous waveform acquisition.",
        primary_packets=("META", "DATA", "STAT", "ERR"),
        rate_guidance="Use when the lab needs roughly 100 to 1000 samples/s.",
        plotting_guidance="Live plotting can usually follow the incoming stream directly.",
    ),
    AcquisitionClass.PHASED_CYCLE: PatternDefinition(
        acquisition_class=AcquisitionClass.PHASED_CYCLE,
        summary="Multi-phase acquisition with one reconstructed output per cycle.",
        primary_packets=("META", "PHASE", "CYCLE", "STAT", "ERR"),
        rate_guidance="Use when several timed phases produce one meaningful cycle result.",
        plotting_guidance="Plot corrected cycle values and keep raw phase logging available for review.",
    ),
}
