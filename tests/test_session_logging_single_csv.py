import csv
import tempfile
import unittest
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = REPO_ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from acquisition.protocol import DataPacket, PhasePacket
from acquisition.session_logging import SessionCsvLogger, create_named_session_paths


class SessionLoggingSingleCsvTests(unittest.TestCase):
    def test_named_session_paths_use_one_csv_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_name:
            output_dir = Path(temp_dir_name)
            paths = create_named_session_paths(output_dir, "example_session")
            self.assertEqual(paths.session_csv_path.name, "example_session.csv")

    def test_session_csv_logger_writes_meta_data_phase_and_errors_to_one_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_name:
            csv_path = Path(temp_dir_name) / "session.csv"
            logger = SessionCsvLogger(
                csv_path,
                data_value_headers=("Signal A",),
                phase_value_headers=("Reflective raw",),
                cycle_value_headers=("Reflective raw (RED corrected)",),
            )
            logger.write_meta("2026-03-23T12:00:00+00:00", 1.0, "board_name", ("Arduino UNO R4 WiFi",))
            logger.write_data(
                DataPacket(
                    host_time_iso="2026-03-23T12:00:01+00:00",
                    host_time_unix_s=2.0,
                    timestamp_field_name="t_ms",
                    device_timestamp=123,
                    field_names=("t_ms", "Signal A"),
                    values=(456,),
                    raw_line="DATA,123,456",
                )
            )
            logger.write_phase(
                PhasePacket(
                    host_time_iso="2026-03-23T12:00:02+00:00",
                    host_time_unix_s=3.0,
                    device_time_us=789,
                    cycle_index=4,
                    phase_name="RED_ON",
                    field_names=("Reflective raw",),
                    values=(321,),
                    raw_line="PHASE,789,4,RED_ON,321",
                )
            )
            logger.write_error("2026-03-23T12:00:03+00:00", 4.0, "Malformed packet", "BAD,LINE")
            logger.close()

            with csv_path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["row_type"], "META")
        self.assertEqual(rows[1]["row_type"], "DATA")
        self.assertEqual(rows[1]["Signal A"], "456")
        self.assertEqual(rows[2]["row_type"], "PHASE")
        self.assertEqual(rows[2]["phase"], "RED_ON")
        self.assertEqual(rows[2]["Reflective raw"], "321")
        self.assertEqual(rows[3]["row_type"], "PARSE_ERROR")
        self.assertEqual(rows[3]["error_message"], "Malformed packet")

    def test_named_session_paths_adds_suffix_on_collision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_name:
            output_dir = Path(temp_dir_name)
            first = create_named_session_paths(output_dir, "example_session")
            first.session_csv_path.touch()

            second = create_named_session_paths(output_dir, "example_session")
            self.assertEqual(second.session_csv_path.name, "example_session_1.csv")
            self.assertEqual(second.output_basename, "example_session_1")


if __name__ == "__main__":
    unittest.main()
