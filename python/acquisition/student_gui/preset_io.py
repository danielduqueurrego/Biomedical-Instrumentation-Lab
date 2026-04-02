from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from acquisition.gui_models import SignalConfiguration, validate_signal_configurations
from acquisition.presets import (
    continuous_timestamp_field_name_for_rate_hz,
    default_sample_rate_hz_for_signal_configurations,
)
from acquisition.protocol import pulseox_cycle_display_names
from acquisition.runtime_paths import writable_app_root
from acquisition.student_gui.constants import DEFAULT_OUTPUT_DIR, DEFAULT_SESSION_PRESET_DIR


SESSION_PRESET_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class SessionPreset:
    preset_name: str
    lab_profile_name: str | None
    acquisition_class: str
    generated_rate_hz: int | None
    timestamp_field_name: str | None
    board_name: str
    save_folder: str
    output_basename_prefix: str
    signals: tuple[SignalConfiguration, ...]
    plot_subplot_count: int
    plot_series_names: tuple[str, ...]
    plot_selected_series_indices: tuple[tuple[int, ...], ...]
    schema_version: int = SESSION_PRESET_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "preset_name": self.preset_name,
            "lab_profile_name": self.lab_profile_name,
            "acquisition_class": self.acquisition_class,
            "generated_rate_hz": self.generated_rate_hz,
            "timestamp_field_name": self.timestamp_field_name,
            "board_name": self.board_name,
            "save_folder": self.save_folder,
            "output_basename_prefix": self.output_basename_prefix,
            "signals": [
                {
                    "name": signal.name,
                    "preset_name": signal.preset_name,
                    "analog_port": signal.analog_port,
                }
                for signal in self.signals
            ],
            "plot": {
                "subplot_count": self.plot_subplot_count,
                "series_names": list(self.plot_series_names),
                "selected_series_indices": [list(indices) for indices in self.plot_selected_series_indices],
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SessionPreset":
        schema_version = int(data.get("schema_version", 0))
        if schema_version != SESSION_PRESET_SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported session preset schema version {schema_version}. "
                f"Expected {SESSION_PRESET_SCHEMA_VERSION}."
            )

        raw_signals = data.get("signals")
        if not isinstance(raw_signals, list) or not raw_signals:
            raise ValueError("Session preset needs a non-empty 'signals' list.")

        signals = []
        for raw_signal in raw_signals:
            if not isinstance(raw_signal, dict):
                raise ValueError("Each signal entry must be an object.")

            signals.append(
                SignalConfiguration(
                    name=str(raw_signal.get("name", "")).strip(),
                    preset_name=str(raw_signal.get("preset_name", "")).strip(),
                    analog_port=str(raw_signal.get("analog_port", "")).strip(),
                )
            )

        signal_configurations = tuple(signals)
        validate_signal_configurations(signal_configurations)

        raw_plot = data.get("plot", {})
        if not isinstance(raw_plot, dict):
            raise ValueError("The 'plot' field must be an object.")

        raw_selected_series_indices = raw_plot.get("selected_series_indices", [])
        if not isinstance(raw_selected_series_indices, list):
            raise ValueError("The plot selected_series_indices field must be a list.")

        selected_series_indices = []
        for row in raw_selected_series_indices:
            if not isinstance(row, list):
                raise ValueError("Each plot selection row must be a list of indices.")
            selected_series_indices.append(tuple(int(index) for index in row))

        raw_series_names = raw_plot.get("series_names", [])
        if raw_series_names and not isinstance(raw_series_names, list):
            raise ValueError("The plot series_names field must be a list.")

        return cls(
            preset_name=str(data.get("preset_name", "Session Preset")).strip() or "Session Preset",
            lab_profile_name=_optional_string(data.get("lab_profile_name")),
            acquisition_class=str(data.get("acquisition_class", "")).strip(),
            generated_rate_hz=_optional_int(data.get("generated_rate_hz")),
            timestamp_field_name=_optional_string(data.get("timestamp_field_name")),
            board_name=str(data.get("board_name", "Arduino UNO R4 WiFi")).strip() or "Arduino UNO R4 WiFi",
            save_folder=str(data.get("save_folder", DEFAULT_OUTPUT_DIR.as_posix())).strip()
            or DEFAULT_OUTPUT_DIR.as_posix(),
            output_basename_prefix=str(data.get("output_basename_prefix", "student_session")).strip()
            or "student_session",
            signals=signal_configurations,
            plot_subplot_count=max(1, int(raw_plot.get("subplot_count", 1))),
            plot_series_names=tuple(str(name) for name in raw_series_names),
            plot_selected_series_indices=tuple(selected_series_indices),
        )


def _optional_string(value: object) -> str | None:
    if value in (None, ""):
        return None
    return str(value)


def _optional_int(value: object) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _serialize_path(path: Path) -> str:
    expanded_path = path.expanduser()
    if not expanded_path.is_absolute():
        return expanded_path.as_posix()

    try:
        return expanded_path.relative_to(writable_app_root()).as_posix()
    except ValueError:
        return str(expanded_path)


def resolve_preset_path(path_text: str) -> Path:
    candidate_path = Path(path_text).expanduser()
    if candidate_path.is_absolute():
        return candidate_path
    return writable_app_root() / candidate_path


def derive_preset_metadata(signal_configurations: tuple[SignalConfiguration, ...]) -> tuple[str, int | None, str | None]:
    validate_signal_configurations(signal_configurations)

    if signal_configurations and all(signal.preset_name == "PulseOx" for signal in signal_configurations):
        return "PHASED_CYCLE", default_sample_rate_hz_for_signal_configurations(signal_configurations), "t_us"

    generated_rate_hz = default_sample_rate_hz_for_signal_configurations(signal_configurations)
    acquisition_class = "CONT_HIGH" if continuous_timestamp_field_name_for_rate_hz(generated_rate_hz) == "t_us" else "CONT_MED"
    timestamp_field_name = continuous_timestamp_field_name_for_rate_hz(generated_rate_hz)
    return acquisition_class, generated_rate_hz, timestamp_field_name


def default_plot_series_names(signal_configurations: tuple[SignalConfiguration, ...]) -> tuple[str, ...]:
    if signal_configurations and all(signal.preset_name == "PulseOx" for signal in signal_configurations):
        return pulseox_cycle_display_names(tuple(signal.name.strip() for signal in signal_configurations))
    return tuple(signal.name.strip() or f"Signal {index + 1}" for index, signal in enumerate(signal_configurations))


def build_session_preset(
    preset_name: str,
    lab_profile_name: str | None,
    board_name: str,
    output_dir: Path,
    output_basename_prefix: str,
    signal_configurations: tuple[SignalConfiguration, ...],
    plot_subplot_count: int,
    plot_selected_series_indices: tuple[tuple[int, ...], ...],
    plot_series_names: tuple[str, ...],
) -> SessionPreset:
    acquisition_class, generated_rate_hz, timestamp_field_name = derive_preset_metadata(signal_configurations)
    return SessionPreset(
        preset_name=preset_name.strip() or "Session Preset",
        lab_profile_name=lab_profile_name,
        acquisition_class=acquisition_class,
        generated_rate_hz=generated_rate_hz,
        timestamp_field_name=timestamp_field_name,
        board_name=board_name,
        save_folder=_serialize_path(output_dir),
        output_basename_prefix=output_basename_prefix.strip() or "student_session",
        signals=signal_configurations,
        plot_subplot_count=max(1, int(plot_subplot_count)),
        plot_series_names=plot_series_names,
        plot_selected_series_indices=plot_selected_series_indices,
    )


def save_session_preset(preset: SessionPreset, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(preset.to_dict(), indent=2) + "\n", encoding="utf-8")


def load_session_preset(input_path: Path) -> SessionPreset:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Session preset JSON root must be an object.")
    return SessionPreset.from_dict(data)
