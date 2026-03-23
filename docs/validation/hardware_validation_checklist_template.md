# Hardware Validation Checklist Template

Use this template as a bench-test record for any lab station.

## Session information

- Date:
- Tester:
- Course or section:
- Lab:
- Board:
- Computer and OS:
- GUI profile or preset used:
- Firmware source:
  - GUI-generated firmware
  - committed reference sketch
- Output basename:

## Hardware setup

- USB cable checked:
- Power source checked:
- Signal board connected:
- Sensor or cuff connected:
- Wiring reviewed against the lab guide:
- Screenshot or photo captured if helpful:

## Target settings

| Item | Target |
| --- | --- |
| Acquisition class | |
| Target sample rate or cycle rate | |
| Expected timestamp field | |
| Expected analog map | |
| Expected packet types | |

## Achieved results

| Item | Observed result | Pass/Needs review |
| --- | --- | --- |
| Achieved sample rate or cycle rate | | |
| Serial connection stayed stable for the run | | |
| Packet loss observed | | |
| Malformed packets observed | | |
| Plot responsiveness acceptable for class use | | |
| Output files created correctly | | |

## Output files reviewed

- `<output>_data.csv` reviewed:
- `<output>_phase.csv` reviewed if applicable:
- `<output>_cycle.csv` reviewed if applicable:
- `<output>_metadata.csv` reviewed:
- `<output>_errors.log` reviewed:

## Bench notes

- Signal quality notes:
- Noise or drift notes:
- Student usability notes:
- Firmware or GUI notes:
- Follow-up actions:

## Suggested evidence to attach

- one GUI setup screenshot
- one live-plot screenshot
- one board or wiring photo
- a short note explaining any parse errors or unstable behavior
