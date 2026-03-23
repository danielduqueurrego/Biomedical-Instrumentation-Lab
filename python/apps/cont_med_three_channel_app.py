import argparse
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from queue import SimpleQueue

import serial

from acquisition.live_plot import ThreeChannelLivePlot
from acquisition.protocol import (
    DEFAULT_THREE_CHANNEL_FIELDS,
    DataPacket,
    PACKET_TYPE_DATA,
    PACKET_TYPE_META,
    PacketParseError,
    UNO_R4_ANALOG_BANK_FIELDS,
    parse_csv_packet,
    parse_data_packet,
    parse_meta_packet,
)
from acquisition.serial_tools import DEFAULT_BAUD_RATE, choose_serial_port, open_serial_connection
from acquisition.session_logging import DataCsvLogger, MetadataLogger, ParseErrorLogger, create_session_paths


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "cont_med" / "three_channel_data_demo"
SERIAL_SHUTDOWN_EXCEPTIONS = (serial.SerialException, OSError, TypeError)


class ContMedThreeChannelApp:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.packet_queue: SimpleQueue = SimpleQueue()
        self.stop_event = threading.Event()
        self.shutdown_lock = threading.Lock()
        self.stop_requested = False
        self.resources_closed = False
        self.reader_thread: threading.Thread | None = None
        self.reader_error: Exception | None = None

        self.serial_port_name = choose_serial_port(args.port)
        self.serial_connection = open_serial_connection(self.serial_port_name, args.baud_rate)

        self.session_paths = create_session_paths(args.output_dir)
        self.expected_data_fields = UNO_R4_ANALOG_BANK_FIELDS
        self.selected_field_names = DEFAULT_THREE_CHANNEL_FIELDS
        self.csv_logger = DataCsvLogger(self.session_paths.data_csv_path, self.selected_field_names)
        self.metadata_logger = MetadataLogger(self.session_paths.metadata_csv_path)
        self.parse_error_logger = ParseErrorLogger(self.session_paths.parse_errors_path)

        self.plotter = ThreeChannelLivePlot(
            packet_queue=self.packet_queue,
            channel_labels=self.selected_field_names[1:],
            history_seconds=args.history_seconds,
            update_interval_ms=args.plot_update_ms,
        )

    def run(self) -> int:
        self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.reader_thread.start()

        print(f"Connected to {self.serial_port_name} at {self.args.baud_rate} baud.")
        print(f"Saving data CSV to: {self.session_paths.data_csv_path}")
        print(f"Saving metadata CSV to: {self.session_paths.metadata_csv_path}")
        print(f"Saving parse errors to: {self.session_paths.parse_errors_path}")
        print("Close the plot window to stop acquisition.")

        try:
            self.plotter.show(should_stop=self.stop_event.is_set, on_close=self.stop)
        finally:
            self.stop()
            if self.reader_thread is not None:
                self.reader_thread.join(timeout=2.0)
            self.close_resources()

        if self.reader_error is not None:
            raise RuntimeError(f"Serial acquisition stopped unexpectedly: {self.reader_error}") from self.reader_error

        return 0

    def stop(self) -> None:
        with self.shutdown_lock:
            if self.stop_requested:
                return

            # Let the reader thread leave readline() on timeout. Closing the
            # port from this thread can trip low-level read errors on Linux.
            self.stop_event.set()
            self.stop_requested = True

    def close_resources(self) -> None:
        with self.shutdown_lock:
            if self.resources_closed:
                return

            try:
                if self.serial_connection.is_open:
                    self.serial_connection.close()
            except SERIAL_SHUTDOWN_EXCEPTIONS:
                pass

            self.csv_logger.close()
            self.metadata_logger.close()
            self.parse_error_logger.close()
            self.resources_closed = True

    def _reader_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                raw_bytes = self.serial_connection.readline()
            except SERIAL_SHUTDOWN_EXCEPTIONS as error:
                if not self.stop_event.is_set():
                    self.reader_error = error
                    self.stop_event.set()
                return

            if not raw_bytes:
                continue

            host_time_unix_s = time.time()
            host_time_iso = datetime.now(timezone.utc).isoformat()
            raw_line = raw_bytes.decode("utf-8", errors="replace").strip()

            if not raw_line:
                continue

            try:
                packet = parse_csv_packet(
                    raw_line=raw_line,
                    host_time_iso=host_time_iso,
                    host_time_unix_s=host_time_unix_s,
                )
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
                    f"Unexpected packet type {packet.packet_type!r} for the CONT_MED A0-A2 reference app.",
                    packet.raw_line,
                )
                continue

            try:
                incoming_packet = parse_data_packet(packet, self.expected_data_fields)
            except PacketParseError as error:
                self.parse_error_logger.write_error(host_time_iso, str(error), error.raw_line)
                continue

            data_packet = DataPacket(
                host_time_iso=incoming_packet.host_time_iso,
                host_time_unix_s=incoming_packet.host_time_unix_s,
                timestamp_field_name=self.selected_field_names[0],
                device_timestamp=incoming_packet.device_timestamp,
                field_names=self.selected_field_names,
                values=incoming_packet.values[:3],
                raw_line=incoming_packet.raw_line,
            )
            self.csv_logger.write_sample(data_packet)
            self.packet_queue.put(data_packet)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Connect to a serial port, log the first three UNO R4 analog-bank channels to CSV, and plot them live.",
    )
    parser.add_argument(
        "--port",
        default=None,
        help="Serial port name, for example COM3 or /dev/ttyACM0. If omitted, the app auto-selects when only one port is found.",
    )
    parser.add_argument(
        "--baud-rate",
        type=int,
        default=DEFAULT_BAUD_RATE,
        help=f"Serial baud rate. Default: {DEFAULT_BAUD_RATE}",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Folder for session logs. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--history-seconds",
        type=float,
        default=10.0,
        help="Visible time span in the live plot. Default: 10 seconds.",
    )
    parser.add_argument(
        "--plot-update-ms",
        type=int,
        default=100,
        help="How often the plot refreshes. Default: 100 ms.",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        app = ContMedThreeChannelApp(args)
        return app.run()
    except (RuntimeError, serial.SerialException) as error:
        print(f"Error: {error}")
        return 1
