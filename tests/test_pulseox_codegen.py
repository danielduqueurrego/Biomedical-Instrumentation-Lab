import unittest
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = REPO_ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from acquisition.arduino_codegen import render_generated_analog_capture_sketch
from acquisition.lab_profiles import get_lab_profile


class PulseOxCodegenTests(unittest.TestCase):
    def test_generated_sketch_uses_shared_phase_inputs_and_explicit_cycle_outputs(self) -> None:
        profile = get_lab_profile("Pulse Oximetry")
        sketch = render_generated_analog_capture_sketch(profile.signal_configurations, baud_rate=230400)

        self.assertIn("META,phase_fields,t_us,cycle_idx,phase,reflective_raw,transmission_raw,reflective_filtered,transmission_filtered", sketch)
        self.assertIn(
            "META,cycle_fields,t_us,cycle_idx,reflective_raw_red_corr,reflective_raw_ir_corr,"
            "transmission_raw_red_corr,transmission_raw_ir_corr,reflective_filtered_red_corr,"
            "reflective_filtered_ir_corr,transmission_filtered_red_corr,transmission_filtered_ir_corr",
            sketch,
        )
        self.assertIn(
            'Serial.println("META,pulseox_analog_map,reflective_raw=A0,transmission_raw=A1,reflective_filtered=A2,transmission_filtered=A3");',
            sketch,
        )
        self.assertIn("const int ANALOG_INPUT_PINS[] = {A0, A1, A2, A3};", sketch)
        self.assertIn(
            "const long reflectiveRawRedCorrected = phaseSamples[RED_ON][REFLECTIVE_RAW] - phaseSamples[DARK1][REFLECTIVE_RAW];",
            sketch,
        )
        self.assertIn(
            "const long transmissionFilteredIrCorrected = phaseSamples[IR_ON][TRANSMISSION_FILTERED] - phaseSamples[DARK2][TRANSMISSION_FILTERED];",
            sketch,
        )
        self.assertNotIn("pulseox_signal_roles", sketch)
        self.assertNotIn("SIGNAL_ROLE_CODES", sketch)


if __name__ == "__main__":
    unittest.main()
