from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from queue import SimpleQueue

import serial

from acquisition.architecture import AcquisitionClass
from acquisition.gui_models import GuiAcquisitionConfig
from acquisition.presets import (
    continuous_acquisition_class_name_for_rate_hz,
    continuous_timestamp_field_name_for_rate_hz,
    default_sample_rate_hz_for_signal_configurations,
    get_preset,
)
from acquisition.protocol import (
    DataPacket,
    PACKET_TYPE_CYCLE,
    PACKET_TYPE_DATA,
    PACKET_TYPE_ERR,
    PACKET_TYPE_META,
    PACKET_TYPE_PHASE,
    PACKET_TYPE_STAT,
    PacketParseError,
    PULSEOX_ANALOG_MAP_FIELDS,
    PULSEOX_ANALOG_PORTS,
    PULSEOX_CYCLE_VALUE_FIELDS,
    PULSEOX_PHASE_VALUE_FIELDS,
    UNO_R4_ANALOG_PORTS,
    parse_csv_packet,
    parse_cycle_packet,
    parse_data_packet,
    parse_meta_packet,
    parse_phase_packet,
    pulseox_cycle_display_names,
)
from acquisition.serial_tools import open_serial_connection
from acquisition.session_logging import (
    SessionCsvLogger,
    create_named_session_paths,
)


SERIAL_SHUTDOWN_EXCEPTIONS = (serial.SerialException, OSError, TypeError)
CONT_HIGH_SESSION_LOG_FLUSH_EVERY_ROWS = 25
DEFAULT_SESSION_LOG_FLUSH_EVERY_ROWS = 1


@dataclass(frozen=True, slots=True)
class SessionSample:
    device_time_us: int
    values: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class SessionMessage:
    level: str
    text: str


class GuiAcquisitionSession:
    """Background serial reader used by the Tkinter GUI."""

    def __init__(self, config: GuiAcquisitionConfig):
        self.config = config
        self.is_phased_cycle = any(
            get_preset(signal.preset_name).acquisition_class == AcquisitionClass.PHASED_CYCLE
            for signal in config.signal_configurations
        )
        self.selected_analog_ports = tuple(signal.analog_port for signal in config.signal_configurations)
        self.continuous_sample_rate_hz = default_sample_rate_hz_for_signal_configurations(config.signal_configurations)
        self.continuous_acquisition_class = continuous_acquisition_class_name_for_rate_hz(self.continuous_sample_rate_hz)
        self.continuous_timestamp_field_name = continuous_timestamp_field_name_for_rate_hz(self.continuous_sample_rate_hz)

        if self.is_phased_cycle:
            self.selected_analog_ports = PULSEOX_ANALOG_PORTS
            self.selected_field_names = ("t_us", "cycle_idx", *PULSEOX_CYCLE_VALUE_FIELDS)
            self.expected_data_fields = ()
            self.expected_phase_fields = ("t_us", "cycle_idx", "phase", *PULSEOX_PHASE_VALUE_FIELDS)
            self.expected_cycle_fields = ("t_us", "cycle_idx", *PULSEOX_CYCLE_VALUE_FIELDS)
            self.phase_value_fields = PULSEOX_PHASE_VALUE_FIELDS
            self.cycle_value_fields = PULSEOX_CYCLE_VALUE_FIELDS
            signal_names = tuple(signal.name.strip() for signal in config.signal_configurations)
            self.plot_series_names = pulseox_cycle_display_names(signal_names)
        else:
            self.selected_field_names = (
                self.continuous_timestamp_field_name,
                *(signal.name.strip() for signal in config.signal_configurations),
            )
            self.expected_data_fields = (self.continuous_timestamp_field_name, *self.selected_analog_ports)
            self.expected_phase_fields = ()
            self.expected_cycle_fields = ()
            self.phase_value_fields = ()
            self.cycle_value_fields = ()
            self.plot_series_names = self.selected_field_names[1:]

        self.sample_queue: SimpleQueue[SessionSample] = SimpleQueue()
        self.message_queue: SimpleQueue[SessionMessage] = SimpleQueue()

        self.stop_event = threading.Event()
        self.shutdown_lock = threading.Lock()
        self.reader_thread: threading.Thread | None = None
        self.reader_error: Exception | None = None

        self.serial_connection: serial.Serial | None = None
        self.session_logger: SessionCsvLogger | None = None
        self.running = False

    def _session_log_flush_every_rows(self) -> int:
        if self.is_phased_cycle:
            return DEFAULT_SESSION_LOG_FLUSH_EVERY_ROWS
        if self.continuous_acquisition_class == AcquisitionClass.CONT_HIGH.name:
            return CONT_HIGH_SESSION_LOG_FLUSH_EVERY_ROWS
        return DEFAULT_SESSION_LOG_FLUSH_EVERY_ROWS

    def start(self) -> None:
        if self.running:
            raise RuntimeError("Acquisition is already running.")

        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        session_paths = create_named_session_paths(self.config.output_dir, self.config.output_basename)

        try:
            self.serial_connection = open_serial_connection(self.config.port, self.config.baud_rate)
            if self.is_phased_cycle:
                self.session_logger = SessionCsvLogger(
                    session_paths.session_csv_path,
                    phase_value_headers=tuple(signal.name.strip() for signal in self.config.signal_configurations),
                    cycle_value_headers=self.plot_series_names,
                    flush_every_rows=self._session_log_flush_every_rows(),
                )
            else:
                self.session_logger = SessionCsvLogger(
                    session_paths.session_csv_path,
                    data_value_headers=self.selected_field_names[1:],
                    flush_every_rows=self._session_log_flush_every_rows(),
                )

            self._write_session_metadata()

            self.running = True
            self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
            self.reader_thread.start()
        except Exception:
            self.stop()
            self._close_resources()
            raise

        if self.is_phased_cycle:
            self._publish_message(
                "info",
                f"Started PHASED_CYCLE acquisition on {self.config.port}. Saving to {session_paths.session_csv_path.name}.",
            )
        else:
            self._publish_message(
                "info",
                f"Started acquisition on {self.config.port}. Saving to {session_paths.session_csv_path.name}",
            )

    def stop(self) -> None:
        with self.shutdown_lock:
            if not self.running and self.stop_event.is_set():
                return

            self.stop_event.set()

    def join(self, timeout: float | None = None) -> None:
        if self.reader_thread is not None:
            self.reader_thread.join(timeout=timeout)
        self._close_resources()

    def is_running(self) -> bool:
        return self.running

    def _write_session_metadata(self) -> None:
        assert self.session_logger is not None

        host_time_iso = datetime.now(timezone.utc).isoformat()
        host_time_unix_s = time.time()
        if self.is_phased_cycle:
            acquisition_class = "PHASED_CYCLE"
        else:
            acquisition_class = self.continuous_acquisition_class
        self.session_logger.write_meta(host_time_iso, host_time_unix_s, "acquisition_class", (acquisition_class,))
        self.session_logger.write_meta(host_time_iso, host_time_unix_s, "board_name", (self.config.board_name,))
        self.session_logger.write_meta(host_time_iso, host_time_unix_s, "board_fqbn", (self.config.board_fqbn,))
        self.session_logger.write_meta(host_time_iso, host_time_unix_s, "selected_port", (self.config.port,))
        self.session_logger.write_meta(host_time_iso, host_time_unix_s, "baud_rate", (str(self.config.baud_rate),))
        self.session_logger.write_meta(host_time_iso, host_time_unix_s, "available_analog_ports", UNO_R4_ANALOG_PORTS)
        self.session_logger.write_meta(host_time_iso, host_time_unix_s, "selected_analog_ports", self.selected_analog_ports)

        if self.is_phased_cycle:
            self.session_logger.write_meta(host_time_iso, host_time_unix_s, "pulseox_analog_map", PULSEOX_ANALOG_MAP_FIELDS)
            self.session_logger.write_meta(host_time_iso, host_time_unix_s, "expected_phase_fields", self.expected_phase_fields)
            self.session_logger.write_meta(host_time_iso, host_time_unix_s, "expected_cycle_fields", self.expected_cycle_fields)
        else:
            self.session_logger.write_meta(host_time_iso, host_time_unix_s, "selected_fields", self.selected_field_names)

        for index, signal in enumerate(self.config.signal_configurations, start=1):
            self.session_logger.write_meta(host_time_iso, host_time_unix_s, f"signal_{index}_name", (signal.name.strip(),))
            self.session_logger.write_meta(host_time_iso, host_time_unix_s, f"signal_{index}_preset", (signal.preset_name,))
            self.session_logger.write_meta(host_time_iso, host_time_unix_s, f"signal_{index}_analog_port", (signal.analog_port,))

    def _close_resources(self) -> None:
        with self.shutdown_lock:
            if self.serial_connection is not None:
                try:
                    if self.serial_connection.is_open:
                        self.serial_connection.close()
                except SERIAL_SHUTDOWN_EXCEPTIONS:
                    pass
                self.serial_connection = None

            if self.session_logger is not None:
                self.session_logger.close()
                self.session_logger = None

            self.running = False

    def _reader_loop(self) -> None:
        assert self.serial_connection is not None
        assert self.session_logger is not None

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
                    self.session_logger.write_error(host_time_iso, host_time_unix_s, str(error), error.raw_line)
                    continue

                if packet.packet_type == PACKET_TYPE_META:
                    self._handle_meta_packet(packet, host_time_iso)
                    continue

                if packet.packet_type == PACKET_TYPE_STAT:
                    self.session_logger.write_stat(host_time_iso, host_time_unix_s, packet.payload, packet.raw_line)
                    continue

                if packet.packet_type == PACKET_TYPE_ERR:
                    self.session_logger.write_error(
                        host_time_iso,
                        host_time_unix_s,
                        "Device ERR packet",
                        packet.raw_line,
                        row_type="ERR",
                        packet_type=PACKET_TYPE_ERR,
                    )
                    self._publish_message("error", f"Device error: {packet.raw_line}")
                    continue

                if self.is_phased_cycle:
                    self._handle_phased_cycle_packet(packet, host_time_iso)
                else:
                    self._handle_continuous_packet(packet, host_time_iso)
        finally:
            if self.reader_error is None:
                self._publish_message("info", "Acquisition stopped.")
            self.stop_event.set()
            self._close_resources()

    def _handle_meta_packet(self, packet, host_time_iso: str) -> None:
        assert self.session_logger is not None

        key, values = parse_meta_packet(packet)
        self.session_logger.write_meta(host_time_iso, packet.host_time_unix_s, key, values, raw_line=packet.raw_line)

        if not self.is_phased_cycle and key == "fields" and tuple(values) != self.expected_data_fields:
            self.session_logger.write_error(
                host_time_iso,
                packet.host_time_unix_s,
                f"Unexpected DATA field layout {values}. Expected {self.expected_data_fields}.",
                packet.raw_line,
            )

        if self.is_phased_cycle and key == "phase_fields" and tuple(values) != self.expected_phase_fields:
            self.session_logger.write_error(
                host_time_iso,
                packet.host_time_unix_s,
                f"Unexpected PHASE field layout {values}. Expected {self.expected_phase_fields}.",
                packet.raw_line,
            )

        if self.is_phased_cycle and key == "cycle_fields" and tuple(values) != self.expected_cycle_fields:
            self.session_logger.write_error(
                host_time_iso,
                packet.host_time_unix_s,
                f"Unexpected CYCLE field layout {values}. Expected {self.expected_cycle_fields}.",
                packet.raw_line,
            )

    def _handle_continuous_packet(self, packet, host_time_iso: str) -> None:
        assert self.session_logger is not None

        if packet.packet_type != PACKET_TYPE_DATA:
            self.session_logger.write_error(
                host_time_iso,
                packet.host_time_unix_s,
                f"Unexpected packet type {packet.packet_type!r} for the continuous GUI workflow.",
                packet.raw_line,
            )
            return

        try:
            incoming_packet = parse_data_packet(packet, self.expected_data_fields)
        except PacketParseError as error:
            self.session_logger.write_error(host_time_iso, packet.host_time_unix_s, str(error), error.raw_line)
            return

        logged_packet = DataPacket(
            host_time_iso=incoming_packet.host_time_iso,
            host_time_unix_s=incoming_packet.host_time_unix_s,
            timestamp_field_name=self.selected_field_names[0],
            device_timestamp=incoming_packet.device_timestamp,
            field_names=self.selected_field_names,
            values=incoming_packet.values,
            raw_line=incoming_packet.raw_line,
        )
        self.session_logger.write_data(logged_packet)
        self.sample_queue.put(SessionSample(device_time_us=logged_packet.device_time_us, values=logged_packet.values))

    def _handle_phased_cycle_packet(self, packet, host_time_iso: str) -> None:
        assert self.session_logger is not None

        if packet.packet_type == PACKET_TYPE_PHASE:
            try:
                phase_packet = parse_phase_packet(packet, self.phase_value_fields)
            except PacketParseError as error:
                self.session_logger.write_error(host_time_iso, packet.host_time_unix_s, str(error), error.raw_line)
                return

            self.session_logger.write_phase(phase_packet)
            return

        if packet.packet_type == PACKET_TYPE_CYCLE:
            try:
                cycle_packet = parse_cycle_packet(packet, self.cycle_value_fields)
            except PacketParseError as error:
                self.session_logger.write_error(host_time_iso, packet.host_time_unix_s, str(error), error.raw_line)
                return

            self.session_logger.write_cycle(cycle_packet)
            self.sample_queue.put(
                SessionSample(
                    device_time_us=cycle_packet.device_time_us,
                    values=cycle_packet.values,
                )
            )
            return

        self.session_logger.write_error(
            host_time_iso,
            packet.host_time_unix_s,
            f"Unexpected packet type {packet.packet_type!r} for the PHASED_CYCLE GUI workflow.",
            packet.raw_line,
        )

    def _publish_message(self, level: str, text: str) -> None:
        self.message_queue.put(SessionMessage(level=level, text=text))
