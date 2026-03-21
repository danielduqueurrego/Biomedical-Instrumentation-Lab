import csv
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from acquisition.protocol import DataPacket


@dataclass(slots=True)
class SessionPaths:
    session_dir: Path
    data_csv_path: Path
    metadata_csv_path: Path
    parse_errors_path: Path


@dataclass(slots=True)
class NamedSessionPaths:
    output_dir: Path
    output_basename: str
    data_csv_path: Path
    metadata_csv_path: Path
    parse_errors_path: Path


def create_session_paths(base_output_dir: Path) -> SessionPaths:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = base_output_dir / timestamp
    session_dir.mkdir(parents=True, exist_ok=False)

    return SessionPaths(
        session_dir=session_dir,
        data_csv_path=session_dir / "data_samples.csv",
        metadata_csv_path=session_dir / "metadata.csv",
        parse_errors_path=session_dir / "parse_errors.log",
    )


def sanitize_output_basename(output_basename: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", output_basename.strip())
    cleaned = cleaned.strip("._")
    return cleaned or "acquisition"


def create_named_session_paths(output_dir: Path, output_basename: str) -> NamedSessionPaths:
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_basename = sanitize_output_basename(output_basename)

    paths = NamedSessionPaths(
        output_dir=output_dir,
        output_basename=safe_basename,
        data_csv_path=output_dir / f"{safe_basename}_data.csv",
        metadata_csv_path=output_dir / f"{safe_basename}_metadata.csv",
        parse_errors_path=output_dir / f"{safe_basename}_errors.log",
    )

    existing_paths = [
        path.name
        for path in (paths.data_csv_path, paths.metadata_csv_path, paths.parse_errors_path)
        if path.exists()
    ]
    if existing_paths:
        joined = ", ".join(existing_paths)
        raise FileExistsError(
            f"The selected output name would overwrite existing files in {output_dir}: {joined}"
        )

    return paths


class DataCsvLogger:
    """Writes every valid DATA sample to CSV and flushes each row for reliability."""

    def __init__(self, csv_path: Path, field_names: tuple[str, ...]):
        self.csv_path = csv_path
        self.field_names = field_names
        self._file = csv_path.open("w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow(
            [
                "host_time_iso",
                "host_time_unix_s",
                "device_time_ms",
                *field_names[1:],
            ]
        )
        self._file.flush()

    def write_sample(self, packet: DataPacket) -> None:
        self._writer.writerow(
            [
                packet.host_time_iso,
                f"{packet.host_time_unix_s:.6f}",
                packet.device_time_ms,
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
