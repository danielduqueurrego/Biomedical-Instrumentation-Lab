import csv
import tempfile
import unittest
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = REPO_ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from acquisition.arduino_codegen import render_generated_analog_capture_sketch
from acquisition.gui_models import GuiAcquisitionConfig
from acquisition.gui_session import GuiAcquisitionSession
from acquisition.lab_profiles import get_lab_profile
from acquisition.presets import get_preset
from acquisition.protocol import parse_csv_packet, parse_data_packet
from acquisition.session_logging import DataCsvLogger


class ContHighConsistencyTests(unittest.TestCase):
    def test_emg_manifest_is_the_canonical_default(self) -> None:
        emg_preset = get_preset("EMG")

        self.assertEqual(emg_preset.default_sample_rate_hz, 2000)
        self.assertEqual(emg_preset.default_fields, ("t_us", "ch1"))

    def test_cont_high_data_packet_parses_microsecond_timestamps(self) -> None:
        raw_line = "DATA,123456,101,202"
        csv_packet = parse_csv_packet(raw_line, "2026-03-23T12:30:00+00:00", 1.0)
        data_packet = parse_data_packet(csv_packet, ("t_us", "A0", "A1"))

        self.assertEqual(data_packet.timestamp_field_name, "t_us")
        self.assertEqual(data_packet.device_timestamp, 123456)
        self.assertEqual(data_packet.device_time_us, 123456)
        self.assertEqual(data_packet.values, (101, 202))

    def test_data_csv_logger_uses_timestamp_header_matching_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            ms_path = temp_dir / "cont_med.csv"
            us_path = temp_dir / "cont_high.csv"

            ms_logger = DataCsvLogger(ms_path, ("t_ms", "A0"))
            ms_logger.close()
            us_logger = DataCsvLogger(us_path, ("t_us", "A0"))
            us_logger.close()

            with ms_path.open(newline="", encoding="utf-8") as handle:
                ms_header = next(csv.reader(handle))
            with us_path.open(newline="", encoding="utf-8") as handle:
                us_header = next(csv.reader(handle))

            self.assertEqual(ms_header[:3], ["host_time_iso", "host_time_unix_s", "device_time_ms"])
            self.assertEqual(us_header[:3], ["host_time_iso", "host_time_unix_s", "device_time_us"])

    def test_generated_emg_sketch_uses_manifest_rate_and_t_us(self) -> None:
        profile = get_lab_profile("EMG")
        sketch = render_generated_analog_capture_sketch(profile.signal_configurations, baud_rate=230400)

        self.assertIn("const unsigned long SAMPLE_RATE_HZ = 2000;", sketch)
        self.assertIn('Serial.println("META,acq_class,CONT_HIGH");', sketch)
        self.assertIn('Serial.println("META,fields,t_us,A0,A1,A2,A3");', sketch)
        self.assertIn("Serial.print(micros());", sketch)

    def test_gui_session_expects_t_us_for_emg(self) -> None:
        profile = get_lab_profile("EMG")
        config = GuiAcquisitionConfig(
            board_name="Arduino UNO R4 WiFi",
            board_fqbn="arduino:renesas_uno:unor4wifi",
            port="/dev/null",
            output_dir=REPO_ROOT,
            output_basename="emg_test",
            baud_rate=230400,
            signal_configurations=profile.signal_configurations,
        )

        session = GuiAcquisitionSession(config)

        self.assertEqual(session.continuous_acquisition_class, "CONT_HIGH")
        self.assertEqual(session.expected_data_fields, ("t_us", "A0", "A1", "A2", "A3"))
        self.assertEqual(session.selected_field_names[0], "t_us")

    def test_committed_emg_reference_sketch_matches_manifest(self) -> None:
        sketch_path = (
            REPO_ROOT
            / "firmware"
            / "cont_high"
            / "uno_r4_wifi"
            / "emg_four_channel_demo"
            / "emg_four_channel_demo.ino"
        )
        sketch_text = sketch_path.read_text(encoding="utf-8")

        self.assertIn("const unsigned long SAMPLE_RATE_HZ = 2000;", sketch_text)
        self.assertIn('Serial.println("META,fields,t_us,A0,A1,A2,A3");', sketch_text)
        self.assertIn('Serial.println("META,acq_class,CONT_HIGH");', sketch_text)
        self.assertIn("Serial.print(nowUs);", sketch_text)

    def test_committed_emg_high_rate_helper_sketch_uses_t_us(self) -> None:
        sketch_path = (
            REPO_ROOT
            / "firmware"
            / "cont_high"
            / "uno_r4_wifi"
            / "emg_high_rate_reference"
            / "emg_high_rate_reference.ino"
        )
        sketch_text = sketch_path.read_text(encoding="utf-8")

        self.assertIn('Serial.println("META,fields,t_us,EMG_A0,EMG_A1");', sketch_text)
        self.assertIn("Serial.print(nowUs);", sketch_text)


if __name__ == "__main__":
    unittest.main()
