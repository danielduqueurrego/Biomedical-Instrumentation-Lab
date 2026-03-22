from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from queue import SimpleQueue

import serial

from acquisition.gui_models import GuiAcquisitionConfig
from acquisition.protocol import (
    DataPacket,
    PACKET_TYPE_DATA,
    PACKET_TYPE_META,
    PacketParseError,
    UNO_R4_ANALOG_BANK_FIELDS,
    UNO_R4_ANALOG_INDEX,
    parse_csv_packet,
    parse_data_packet,
    parse_meta_packet,
)
from acquisition.serial_tools import open_serial_connection
from acquisition.session_logging import DataCsvLogger, MetadataLogger, ParseErrorLogger, create_named_session_paths


SERIAL_SHUTDOWN_EXCEPTIONS = (serial.SerialException, OSError, TypeError)


@dataclass(frozen=True, slots=True)
class SessionSample:
    device_time_ms: int
    values: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class SessionMessage:
    level: str
    text: str


class GuiAcquisitionSession:
    """Background serial reader used by the Tkinter GUI."""

    def __init__(self, config: GuiAcquisitionConfig):
        self.config = config
        self.expected_data_fields = UNO_R4_ANALOG_BANK_FIELDS
        self.selected_field_names = ("t_ms", *(signal.name.strip() for signal in config.signal_configurations))
        self.selected_analog_ports = tuple(signal.analog_port for signal in config.signal_configurations)
        self.selected_value_indexes = tuple(UNO_R4_ANALOG_INDEX[port_name] for port_name in self.selected_analog_ports)

        self.sample_queue: SimpleQueue[SessionSample] = SimpleQueue()
        self.message_queue: SimpleQueue[SessionMessage] = SimpleQueue()

        self.stop_event = threading.Event()
        self.shutdown_lock = threading.Lock()
        self.reader_thread: threading.Thread | None = None
        self.reader_error: Exception | None = None

        self.serial_connection: serial.Serial | None = None
        self.csv_logger: DataCsvLogger | None = None
        self.metadata_logger: MetadataLogger | None = None
        self.parse_error_logger: ParseErrorLogger | None = None
        self.running = False

    def start(self) -> None:
        if self.running:
            raise RuntimeError("Acquisition is already running.")

        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        session_paths = create_named_session_paths(self.config.output_dir, self.config.output_basename)

        try:
            self.serial_connection = open_serial_connection(self.config.port, self.config.baud_rate)
            self.csv_logger = DataCsvLogger(session_paths.data_csv_path, self.selected_field_names)
            self.metadata_logger = MetadataLogger(session_paths.metadata_csv_path)
            self.parse_error_logger = ParseErrorLogger(session_paths.parse_errors_path)

            self._write_session_metadata()

            self.running = True
            self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
            self.reader_thread.start()
        except Exception:
            self.stop()
            self._close_resources()
            raise

        self._publish_message(
            "info",
            f"Started acquisition on {self.config.port}. Saving to {session_paths.data_csv_path.name}",
        )

    def stop(self) -> None:
        with self.shutdown_lock:
            if not self.running and self.stop_event.is_set():
                return

            # Let the reader thread leave readline() on its next timeout and
            # close the serial port itself. Closing from this thread can raise
            # low-level read errors on Linux while os.read() is still active.
            self.stop_event.set()

    def join(self, timeout: float | None = None) -> None:
        if self.reader_thread is not None:
            self.reader_thread.join(timeout=timeout)
        self._close_resources()

    def is_running(self) -> bool:
        return self.running

    def _write_session_metadata(self) -> None:
        assert self.metadata_logger is not None

        host_time_iso = datetime.now(timezone.utc).isoformat()
        self.metadata_logger.write_meta(host_time_iso, "board_name", (self.config.board_name,))
        self.metadata_logger.write_meta(host_time_iso, "board_fqbn", (self.config.board_fqbn,))
        self.metadata_logger.write_meta(host_time_iso, "selected_port", (self.config.port,))
        self.metadata_logger.write_meta(host_time_iso, "baud_rate", (str(self.config.baud_rate),))
        self.metadata_logger.write_meta(host_time_iso, "selected_fields", self.selected_field_names)
        self.metadata_logger.write_meta(host_time_iso, "available_analog_ports", self.expected_data_fields[1:])

        for index, signal in enumerate(self.config.signal_configurations, start=1):
            self.metadata_logger.write_meta(host_time_iso, f"signal_{index}_name", (signal.name.strip(),))
            self.metadata_logger.write_meta(host_time_iso, f"signal_{index}_preset", (signal.preset_name,))
            self.metadata_logger.write_meta(host_time_iso, f"signal_{index}_analog_port", (signal.analog_port,))

    def _close_resources(self) -> None:
        with self.shutdown_lock:
            if self.serial_connection is not None:
                try:
                    if self.serial_connection.is_open:
                        self.serial_connection.close()
                except SERIAL_SHUTDOWN_EXCEPTIONS:
                    pass
                self.serial_connection = None

            if self.csv_logger is not None:
                self.csv_logger.close()
                self.csv_logger = None

            if self.metadata_logger is not None:
                self.metadata_logger.close()
                self.metadata_logger = None

            if self.parse_error_logger is not None:
                self.parse_error_logger.close()
                self.parse_error_logger = None

            self.running = False

    def _reader_loop(self) -> None:
        assert self.serial_connection is not None
        assert self.csv_logger is not None
        assert self.metadata_logger is not None
        assert self.parse_error_logger is not None

        try:
            while not self.stop_event.is_set():
                try:
                    raw_bytes = self.serial_connection.readline()
                except SERIAL_SHUTDOWN_EXCEPTIONS as error:
                    if not self.stop_event.is_set():
                        self.reader_error = error
                        self._publish_message("error", f"Serial error: {error}")
                    break

                if not raw_bytes:
                    continue

                host_time_unix_s = time.time()
                host_time_iso = datetime.now(timezone.utc).isoformat()
                raw_line = raw_bytes.decode("utf-8", errors="replace").strip()

                if not raw_line:
                    continue

                try:
                    packet = parse_csv_packet(raw_line, host_time_iso, host_time_unix_s)
                except PacketParseError as error:
                    self.parse_error_logger.write_error(host_time_iso, str(error), error.raw_line)
                    continue

                if packet.packet_type == PACKET_TYPE_META:
                    key, values = parse_meta_packet(packet)
                    self.metadata_logger.write_meta(host_time_iso, key, values)

                    if key == "fields" and tuple(values) != self.expected_data_fields:
                        self.parse_error_logger.write_error(
                            host_time_iso,
                            f"Unexpected DATA field layout {values}. Expected {self.expected_data_fields}.",
                            packet.raw_line,
                        )
                    continue

                if packet.packet_type != PACKET_TYPE_DATA:
                    self.parse_error_logger.write_error(
                        host_time_iso,
                        f"Unexpected packet type {packet.packet_type!r} for the GUI foundation app.",
                        packet.raw_line,
                    )
                    continue

                try:
                    incoming_packet = parse_data_packet(packet, self.expected_data_fields)
                except PacketParseError as error:
                    self.parse_error_logger.write_error(host_time_iso, str(error), error.raw_line)
                    continue

                selected_values = tuple(incoming_packet.values[index] for index in self.selected_value_indexes)
                logged_packet = DataPacket(
                    host_time_iso=incoming_packet.host_time_iso,
                    host_time_unix_s=incoming_packet.host_time_unix_s,
                    device_time_ms=incoming_packet.device_time_ms,
                    field_names=self.selected_field_names,
                    values=selected_values,
                    raw_line=incoming_packet.raw_line,
                )
                self.csv_logger.write_sample(logged_packet)
                self.sample_queue.put(
                    SessionSample(device_time_ms=logged_packet.device_time_ms, values=logged_packet.values)
                )
        finally:
            if self.reader_error is None:
                self._publish_message("info", "Acquisition stopped.")
            self.stop_event.set()
            self._close_resources()

    def _publish_message(self, level: str, text: str) -> None:
        self.message_queue.put(SessionMessage(level=level, text=text))
