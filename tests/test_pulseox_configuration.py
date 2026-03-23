import unittest
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = REPO_ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from acquisition.gui_models import GuiAcquisitionConfig, SignalConfiguration, validate_signal_configurations
from acquisition.gui_session import GuiAcquisitionSession
from acquisition.lab_profiles import get_lab_profile
from acquisition.protocol import (
    PULSEOX_CYCLE_VALUE_FIELDS,
    PULSEOX_PHASE_VALUE_FIELDS,
    pulseox_cycle_display_names,
)


class PulseOxConfigurationTests(unittest.TestCase):
    def test_lab_profile_uses_fixed_four_channel_mapping(self) -> None:
        profile = get_lab_profile("Pulse Oximetry")

        self.assertEqual(len(profile.signal_configurations), 4)
        self.assertEqual(
            tuple(signal.analog_port for signal in profile.signal_configurations),
            ("A0", "A1", "A2", "A3"),
        )
        validate_signal_configurations(profile.signal_configurations)

    def test_pulseox_validation_rejects_wrong_port_order(self) -> None:
        with self.assertRaisesRegex(ValueError, "must keep the analog ports in this order"):
            validate_signal_configurations(
                (
                    SignalConfiguration("Reflective photodiode raw output", "PulseOx", "A1"),
                    SignalConfiguration("Transmission photodiode raw output", "PulseOx", "A0"),
                    SignalConfiguration("Filtered reflective photodiode output", "PulseOx", "A2"),
                    SignalConfiguration("Filtered transmission photodiode output", "PulseOx", "A3"),
                )
            )

    def test_session_exposes_pulseox_protocol_fields_and_plot_labels(self) -> None:
        profile = get_lab_profile("Pulse Oximetry")
        config = GuiAcquisitionConfig(
            board_name="Arduino UNO R4 WiFi",
            board_fqbn="arduino:renesas_uno:unor4wifi",
            port="/dev/null",
            output_dir=Path("."),
            output_basename="test_session",
            baud_rate=230400,
            signal_configurations=profile.signal_configurations,
        )

        session = GuiAcquisitionSession(config)

        self.assertEqual(
            session.expected_phase_fields,
            ("t_us", "cycle_idx", "phase", *PULSEOX_PHASE_VALUE_FIELDS),
        )
        self.assertEqual(
            session.expected_cycle_fields,
            ("t_us", "cycle_idx", *PULSEOX_CYCLE_VALUE_FIELDS),
        )
        self.assertEqual(session.cycle_value_fields, PULSEOX_CYCLE_VALUE_FIELDS)
        self.assertEqual(
            session.plot_series_names,
            pulseox_cycle_display_names(tuple(signal.name for signal in profile.signal_configurations)),
        )


if __name__ == "__main__":
    unittest.main()
