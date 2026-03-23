import unittest
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = REPO_ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from acquisition.protocol import (
    PULSEOX_ANALOG_MAP_FIELDS,
    PULSEOX_ANALOG_PORTS,
    PULSEOX_CYCLE_VALUE_FIELDS,
    PULSEOX_PHASE_VALUE_FIELDS,
    parse_csv_packet,
    parse_cycle_packet,
    parse_phase_packet,
)


class PulseOxProtocolTests(unittest.TestCase):
    def test_phase_packet_parses_four_shared_optical_channels(self) -> None:
        raw_line = "PHASE,125000,312,RED_ON,1842,1760,1901,1888"
        csv_packet = parse_csv_packet(raw_line, "2026-03-23T12:00:00+00:00", 1.0)
        phase_packet = parse_phase_packet(csv_packet, PULSEOX_PHASE_VALUE_FIELDS)

        self.assertEqual(PULSEOX_ANALOG_PORTS, ("A0", "A1", "A2", "A3"))
        self.assertEqual(
            PULSEOX_ANALOG_MAP_FIELDS,
            (
                "reflective_raw=A0",
                "transmission_raw=A1",
                "reflective_filtered=A2",
                "transmission_filtered=A3",
            ),
        )
        self.assertEqual(phase_packet.phase_name, "RED_ON")
        self.assertEqual(phase_packet.field_names, PULSEOX_PHASE_VALUE_FIELDS)
        self.assertEqual(phase_packet.values, (1842, 1760, 1901, 1888))

    def test_cycle_packet_parses_eight_corrected_outputs(self) -> None:
        raw_line = "CYCLE,127550,312,82,61,74,53,45,38,41,29"
        csv_packet = parse_csv_packet(raw_line, "2026-03-23T12:00:01+00:00", 2.0)
        cycle_packet = parse_cycle_packet(csv_packet, PULSEOX_CYCLE_VALUE_FIELDS)

        self.assertEqual(
            cycle_packet.field_names,
            (
                "reflective_raw_red_corr",
                "reflective_raw_ir_corr",
                "transmission_raw_red_corr",
                "transmission_raw_ir_corr",
                "reflective_filtered_red_corr",
                "reflective_filtered_ir_corr",
                "transmission_filtered_red_corr",
                "transmission_filtered_ir_corr",
            ),
        )
        self.assertEqual(cycle_packet.values, (82, 61, 74, 53, 45, 38, 41, 29))


if __name__ == "__main__":
    unittest.main()
