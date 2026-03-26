# Pulse Oximetry Lab

> Multi-phase optical workflow that logs raw phase measurements and corrected cycle values.

Use this guide when you are running the PulseOx lab, validating the optical timing, or checking whether the current hardware model matches the board.

---

## Start Here

Recommended classroom path:

1. connect the Arduino UNO R4 WiFi
2. launch the student GUI
3. choose `Pulse Oximetry` from the lab dropdown or load `python/session_presets/pulse_ox.json`
4. confirm the four PulseOx rows are locked to `A0` to `A3`
5. choose a save folder
6. compile and upload from the GUI or use the committed PulseOx reference sketch
7. start acquisition

---

## Quick Reference

| Item | Current default |
| --- | --- |
| Purpose | Show raw optical phase behavior and corrected red/IR cycle values |
| Acquisition class | `PHASED_CYCLE` |
| Default cycle rate | `100 cycles/s` |
| Default phase rate | `400 phase samples/s` |
| Arduino timestamp field | `t_us` |
| Main packet types | `META`, `PHASE`, `CYCLE`, optional `STAT`, optional `ERR` |
| Student preset | `python/session_presets/pulse_ox.json` |
| Reference sketch | `firmware/phased_cycle/uno_r4_wifi/pulse_ox_reference/pulse_ox_reference.ino` |

---

## Hardware Model And Pin Mapping

Current UNO R4 WiFi PulseOx mapping:

- `A0 = Reflective photodiode raw output`
- `A1 = Transmission photodiode raw output`
- `A2 = Filtered reflective photodiode output`
- `A3 = Filtered transmission photodiode output`
- `D6 = RED LED control`
- `D5 = IR LED control`

Important rule:

- red versus IR is not determined by separate analog pins
- red versus IR is determined by LED timing phase

Phase sequence:

- `RED_ON`
- `DARK1`
- `IR_ON`
- `DARK2`

During every phase, the firmware samples all four analog inputs.

---

## Firmware And GUI Notes

Current behavior to remember:

- PulseOx uses `PHASED_CYCLE`, not continuous `DATA`
- the GUI stores `PHASE` and `CYCLE` rows in the same session CSV
- the live plot shows corrected `CYCLE` values by default
- generated firmware uses settled ADC reads to reduce channel-switching spikes

PulseOx generated and reference firmware both follow the same hardware model and packet semantics.

---

## Expected Output

The session CSV should contain:

- `META` rows for cycle rate, phase rate, analog map, LED pins, and field declarations
- `PHASE` rows with all four analog channel readings during each phase
- `CYCLE` rows with corrected red and IR outputs for each optical path
- optional `STAT`, `ERR`, or `PARSE_ERROR` rows if relevant

Students should usually start by filtering to:

- `row_type=CYCLE`

When debugging optical timing or LED behavior, also inspect:

- `row_type=PHASE`

---

## Troubleshooting

### The plot labels do not match the expected channels

- reload the PulseOx preset
- confirm the four fixed PulseOx channel names are loaded in the left panel

### There are strange peaks or spikes

- confirm you uploaded current firmware, not an older PulseOx sketch
- current firmware discards the first ADC read after channel switching and averages two settled reads
- if the spikes remain, record a short validation session and inspect both `PHASE` and `CYCLE` rows

### The session looks like continuous data instead of phases

- confirm the selected lab is actually `Pulse Oximetry`
- confirm the metadata reports `acq_class,PHASED_CYCLE`

---

## Screenshot Placeholder

Recommended screenshot location:

- `docs/screenshots/pulse_ox_live_plot_placeholder.svg`

Replace it later with a real classroom capture when available.

---

## See Also

- [Lab index](./README.md)
- [Generated firmware workflow](../generated_firmware_workflow.md)
- [Serial protocol](../serial_protocol.md)
- [Validation tables](../validation/lab_validation_tables.md)
