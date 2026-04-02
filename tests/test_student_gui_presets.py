import tempfile
import unittest
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = REPO_ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from acquisition.lab_profiles import CUSTOM_LAB_PROFILE_NAME, LAB_PROFILE_ORDER, get_lab_profile
from acquisition.student_gui.constants import DEFAULT_OUTPUT_DIR
from acquisition.student_gui.preset_io import (
    SessionPreset,
    build_session_preset,
    default_plot_series_names,
    derive_preset_metadata,
    load_session_preset,
    resolve_preset_path,
    save_session_preset,
)


class StudentGuiPresetTests(unittest.TestCase):
    def test_lab_profile_order_includes_custom_first(self) -> None:
        self.assertGreaterEqual(len(LAB_PROFILE_ORDER), 1)
        self.assertEqual(LAB_PROFILE_ORDER[0], CUSTOM_LAB_PROFILE_NAME)

    def test_session_preset_roundtrip_preserves_emg_configuration(self) -> None:
        profile = get_lab_profile("EMG")
        plot_series_names = default_plot_series_names(profile.signal_configurations)
        preset = build_session_preset(
            preset_name="EMG Lab",
            lab_profile_name=profile.display_name,
            board_name="Arduino UNO R4 WiFi",
            output_dir=REPO_ROOT / "data" / "gui_sessions",
            output_basename_prefix="emg_lab",
            signal_configurations=profile.signal_configurations,
            plot_subplot_count=2,
            plot_selected_series_indices=((0, 1), (2, 3)),
            plot_series_names=plot_series_names,
        )

        with tempfile.TemporaryDirectory() as temp_dir_name:
            output_path = Path(temp_dir_name) / "emg_preset.json"
            save_session_preset(preset, output_path)
            loaded_preset = load_session_preset(output_path)

        self.assertEqual(loaded_preset, preset)
        self.assertEqual(resolve_preset_path(loaded_preset.save_folder), REPO_ROOT / "data" / "gui_sessions")

    def test_example_preset_files_match_lab_profiles(self) -> None:
        expected_files = {
            "EMG": "emg.json",
            "ECG": "ecg.json",
            "Pulse Oximetry": "pulse_ox.json",
            "Blood Pressure": "blood_pressure.json",
        }

        for profile_name, file_name in expected_files.items():
            with self.subTest(profile=profile_name):
                preset = load_session_preset(REPO_ROOT / "python" / "session_presets" / file_name)
                profile = get_lab_profile(profile_name)
                expected_acquisition_class, expected_rate_hz, expected_timestamp = derive_preset_metadata(
                    profile.signal_configurations
                )

                self.assertEqual(preset.lab_profile_name, profile_name)
                self.assertEqual(preset.signals, profile.signal_configurations)
                self.assertEqual(preset.acquisition_class, expected_acquisition_class)
                self.assertEqual(preset.generated_rate_hz, expected_rate_hz)
                self.assertEqual(preset.timestamp_field_name, expected_timestamp)
                self.assertEqual(preset.plot_series_names, default_plot_series_names(profile.signal_configurations))
                self.assertEqual(preset.plot_subplot_count, len(preset.plot_selected_series_indices))

    def test_missing_save_folder_defaults_to_gui_output_directory(self) -> None:
        preset = SessionPreset.from_dict(
            {
                "schema_version": 1,
                "preset_name": "Custom ECG",
                "lab_profile_name": None,
                "acquisition_class": "CONT_MED",
                "generated_rate_hz": 500,
                "timestamp_field_name": "t_ms",
                "board_name": "Arduino UNO R4 WiFi",
                "output_basename_prefix": "custom_ecg",
                "signals": [
                    {
                        "name": "Lead II",
                        "preset_name": "ECG",
                        "analog_port": "A0",
                    }
                ],
                "plot": {
                    "subplot_count": 1,
                    "series_names": ["Lead II"],
                    "selected_series_indices": [[0]],
                },
            }
        )

        self.assertEqual(resolve_preset_path(preset.save_folder), DEFAULT_OUTPUT_DIR)


if __name__ == "__main__":
    unittest.main()
