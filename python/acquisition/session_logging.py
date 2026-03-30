import csv
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from acquisition.protocol import CyclePacket, DataPacket, PhasePacket


@dataclass(slots=True)
class SessionPaths:
    session_dir: Path
    session_csv_path: Path


@dataclass(slots=True)
class NamedSessionPaths:
    output_dir: Path
    output_basename: str
    session_csv_path: Path


def create_session_paths(base_output_dir: Path) -> SessionPaths:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = base_output_dir / timestamp
    session_dir.mkdir(parents=True, exist_ok=False)

    return SessionPaths(
        session_dir=session_dir,
        session_csv_path=session_dir / "session.csv",
    )


def sanitize_output_basename(output_basename: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", output_basename.strip())
    cleaned = cleaned.strip("._")
    return cleaned or "acquisition"


def create_named_session_paths(output_dir: Path, output_basename: str) -> NamedSessionPaths:
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_basename = sanitize_output_basename(output_basename)
    candidate_basename = safe_basename
    candidate_path = output_dir / f"{candidate_basename}.csv"
    suffix = 1

    while candidate_path.exists():
        candidate_basename = f"{safe_basename}_{suffix}"
        candidate_path = output_dir / f"{candidate_basename}.csv"
        suffix += 1

    return NamedSessionPaths(
        output_dir=output_dir,
        output_basename=candidate_basename,
        session_csv_path=candidate_path,
    )


class SessionCsvLogger:
    """Write one student-facing CSV per session, regardless of acquisition mode."""

    BASE_COLUMNS = (
        "row_type",
        "packet_type",
        "host_time_iso",
        "host_time_unix_s",
        "device_timestamp_field",
        "device_timestamp",
        "cycle_idx",
        "phase",
        "meta_key",
        "meta_values",
        "error_message",
        "raw_line",
    )

    def __init__(
        self,
        csv_path: Path,
        data_value_headers: tuple[str, ...] = (),
        phase_value_headers: tuple[str, ...] = (),
        cycle_value_headers: tuple[str, ...] = (),
    ):
        self.csv_path = csv_path
        self.data_value_headers = data_value_headers
        self.phase_value_headers = phase_value_headers
        self.cycle_value_headers = cycle_value_headers
        self._file = csv_path.open("w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow(
            [
                *self.BASE_COLUMNS,
                *self.data_value_headers,
                *self.phase_value_headers,
                *self.cycle_value_headers,
            ]
        )
        self._file.flush()

    def _write_row(
        self,
        *,
        row_type: str,
        packet_type: str = "",
        host_time_iso: str,
        host_time_unix_s: float | str = "",
        device_timestamp_field: str = "",
        device_timestamp: int | str = "",
        cycle_idx: int | str = "",
        phase: str = "",
        meta_key: str = "",
        meta_values: tuple[str, ...] | str = "",
        error_message: str = "",
        raw_line: str = "",
        data_values: tuple[int, ...] = (),
        phase_values: tuple[int, ...] = (),
        cycle_values: tuple[int, ...] = (),
    ) -> None:
        meta_text = "|".join(meta_values) if isinstance(meta_values, tuple) else meta_values
        padded_data_values = [*data_values, *([""] * max(0, len(self.data_value_headers) - len(data_values)))]
        padded_phase_values = [*phase_values, *([""] * max(0, len(self.phase_value_headers) - len(phase_values)))]
        padded_cycle_values = [*cycle_values, *([""] * max(0, len(self.cycle_value_headers) - len(cycle_values)))]
        self._writer.writerow(
            [
                row_type,
                packet_type,
                host_time_iso,
                f"{host_time_unix_s:.6f}" if isinstance(host_time_unix_s, float) else host_time_unix_s,
                device_timestamp_field,
                device_timestamp,
                cycle_idx,
                phase,
                meta_key,
                meta_text,
                error_message,
                raw_line,
                *padded_data_values,
                *padded_phase_values,
                *padded_cycle_values,
            ]
        )
        self._file.flush()

    def write_meta(
        self,
        host_time_iso: str,
        host_time_unix_s: float,
        key: str,
        values: tuple[str, ...],
        raw_line: str = "",
    ) -> None:
        self._write_row(
            row_type="META",
            packet_type="META",
            host_time_iso=host_time_iso,
            host_time_unix_s=host_time_unix_s,
            meta_key=key,
            meta_values=values,
            raw_line=raw_line,
        )

    def write_stat(self, host_time_iso: str, host_time_unix_s: float, values: tuple[str, ...], raw_line: str) -> None:
        self._write_row(
            row_type="STAT",
            packet_type="STAT",
            host_time_iso=host_time_iso,
            host_time_unix_s=host_time_unix_s,
            meta_values=values,
            raw_line=raw_line,
        )

    def write_data(self, packet: DataPacket) -> None:
        self._write_row(
            row_type="DATA",
            packet_type="DATA",
            host_time_iso=packet.host_time_iso,
            host_time_unix_s=packet.host_time_unix_s,
            device_timestamp_field=packet.timestamp_field_name,
            device_timestamp=packet.device_timestamp,
            raw_line=packet.raw_line,
            data_values=packet.values,
        )

    def write_phase(self, packet: PhasePacket) -> None:
        self._write_row(
            row_type="PHASE",
            packet_type="PHASE",
            host_time_iso=packet.host_time_iso,
            host_time_unix_s=packet.host_time_unix_s,
            device_timestamp_field="t_us",
            device_timestamp=packet.device_time_us,
            cycle_idx=packet.cycle_index,
            phase=packet.phase_name,
            raw_line=packet.raw_line,
            phase_values=packet.values,
        )

    def write_cycle(self, packet: CyclePacket) -> None:
        self._write_row(
            row_type="CYCLE",
            packet_type="CYCLE",
            host_time_iso=packet.host_time_iso,
            host_time_unix_s=packet.host_time_unix_s,
            device_timestamp_field="t_us",
            device_timestamp=packet.device_time_us,
            cycle_idx=packet.cycle_index,
            raw_line=packet.raw_line,
            cycle_values=packet.values,
        )

    def write_error(
        self,
        host_time_iso: str,
        host_time_unix_s: float,
        error_message: str,
        raw_line: str,
        row_type: str = "PARSE_ERROR",
        packet_type: str = "",
    ) -> None:
        self._write_row(
            row_type=row_type,
            packet_type=packet_type,
            host_time_iso=host_time_iso,
            host_time_unix_s=host_time_unix_s,
            error_message=error_message,
            raw_line=raw_line,
        )

    def close(self) -> None:
        self._file.close()


class DataCsvLogger:
    """Writes every valid DATA sample to CSV and flushes each row for reliability."""

    def __init__(self, csv_path: Path, field_names: tuple[str, ...]):
        self.csv_path = csv_path
        self.field_names = field_names
        if field_names[0] == "t_us":
            timestamp_header = "device_time_us"
        else:
            timestamp_header = "device_time_ms"
        self._file = csv_path.open("w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow(
            [
                "host_time_iso",
                "host_time_unix_s",
                timestamp_header,
                *field_names[1:],
            ]
        )
        self._file.flush()

    def write_sample(self, packet: DataPacket) -> None:
        self._writer.writerow(
            [
                packet.host_time_iso,
                f"{packet.host_time_unix_s:.6f}",
                packet.device_timestamp,
                *packet.values,
            ]
        )
        self._file.flush()

    def close(self) -> None:
        self._file.close()


class MetadataLogger:
    """Stores META packets so the session keeps its own declared field layout."""

    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self._file = csv_path.open("w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow(["host_time_iso", "key", "values"])
        self._file.flush()

    def write_meta(self, host_time_iso: str, key: str, values: tuple[str, ...]) -> None:
        self._writer.writerow([host_time_iso, key, "|".join(values)])
        self._file.flush()

    def close(self) -> None:
        self._file.close()


class PhaseCsvLogger:
    """Writes every valid PHASE packet to CSV and flushes each row for reliability."""

    def __init__(self, csv_path: Path, field_names: tuple[str, ...]):
        self.csv_path = csv_path
        self.field_names = field_names
        self._file = csv_path.open("w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow(
            [
                "host_time_iso",
                "host_time_unix_s",
                "device_time_us",
                "cycle_idx",
                "phase",
                *field_names,
            ]
        )
        self._file.flush()

    def write_phase(self, packet: PhasePacket) -> None:
        self._writer.writerow(
            [
                packet.host_time_iso,
                f"{packet.host_time_unix_s:.6f}",
                packet.device_time_us,
                packet.cycle_index,
                packet.phase_name,
                *packet.values,
            ]
        )
        self._file.flush()

    def close(self) -> None:
        self._file.close()


class CycleCsvLogger:
    """Writes reconstructed CYCLE packets to CSV and flushes each row for reliability."""

    def __init__(self, csv_path: Path, field_names: tuple[str, ...]):
        self.csv_path = csv_path
        self.field_names = field_names
        self._file = csv_path.open("w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow(
            [
                "host_time_iso",
                "host_time_unix_s",
                "device_time_us",
                "cycle_idx",
                *field_names,
            ]
        )
        self._file.flush()

    def write_cycle(self, packet: CyclePacket) -> None:
        self._writer.writerow(
            [
                packet.host_time_iso,
                f"{packet.host_time_unix_s:.6f}",
                packet.device_time_us,
                packet.cycle_index,
                *packet.values,
            ]
        )
        self._file.flush()

    def close(self) -> None:
        self._file.close()


class ParseErrorLogger:
    """Stores malformed lines so students can inspect serial protocol problems."""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._file = log_path.open("w", encoding="utf-8")
        self._file.write("host_time_iso\terror\traw_line\n")
        self._file.flush()

    def write_error(self, host_time_iso: str, error_message: str, raw_line: str) -> None:
        safe_line = raw_line.replace("\t", " ")
        self._file.write(f"{host_time_iso}\t{error_message}\t{safe_line}\n")
        self._file.flush()

    def close(self) -> None:
        self._file.close()
