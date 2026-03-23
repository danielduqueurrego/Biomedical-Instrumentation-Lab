import unittest
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = REPO_ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))


class PulseOxReferenceSketchTests(unittest.TestCase):
    def test_committed_pulseox_reference_sketch_matches_current_hardware_model(self) -> None:
        sketch_path = (
            REPO_ROOT
            / "firmware"
            / "phased_cycle"
            / "uno_r4_wifi"
            / "pulse_ox_reference"
            / "pulse_ox_reference.ino"
        )
        sketch_text = sketch_path.read_text(encoding="utf-8")

        self.assertIn("const int ANALOG_INPUT_PINS[] = {A0, A1, A2, A3};", sketch_text)
        self.assertIn('Serial.println("META,pulseox_analog_map,reflective_raw=A0,transmission_raw=A1,reflective_filtered=A2,transmission_filtered=A3");', sketch_text)
        self.assertIn('Serial.println("META,pulseox_phase_sequence,RED_ON,DARK1,IR_ON,DARK2");', sketch_text)
        self.assertIn("analogReadResolution(ADC_RESOLUTION_BITS);", sketch_text)
        self.assertIn("int readSettledPulseOxChannel(int analogPin)", sketch_text)


if __name__ == "__main__":
    unittest.main()
