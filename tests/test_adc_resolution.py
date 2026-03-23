import unittest
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = REPO_ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))


class AdcResolutionTests(unittest.TestCase):
    def test_cont_med_reference_sketch_sets_14_bit_adc_resolution(self) -> None:
        sketch_path = (
            REPO_ROOT
            / "firmware"
            / "cont_med"
            / "uno_r4_wifi"
            / "three_channel_data_demo"
            / "three_channel_data_demo.ino"
        )
        sketch_text = sketch_path.read_text(encoding="utf-8")

        self.assertIn("analogReadResolution(14);", sketch_text)
        self.assertIn('Serial.println("META,adc_resolution_bits,14");', sketch_text)

    def test_cont_high_reference_sketches_set_14_bit_adc_resolution(self) -> None:
        sketch_paths = (
            REPO_ROOT
            / "firmware"
            / "cont_high"
            / "uno_r4_wifi"
            / "emg_four_channel_demo"
            / "emg_four_channel_demo.ino",
            REPO_ROOT
            / "firmware"
            / "cont_high"
            / "uno_r4_wifi"
            / "emg_high_rate_reference"
            / "emg_high_rate_reference.ino",
        )

        for sketch_path in sketch_paths:
            with self.subTest(sketch=sketch_path.name):
                sketch_text = sketch_path.read_text(encoding="utf-8")
                self.assertIn("analogReadResolution(14);", sketch_text)
                self.assertIn('Serial.println("META,adc_resolution_bits,14");', sketch_text)


if __name__ == "__main__":
    unittest.main()
