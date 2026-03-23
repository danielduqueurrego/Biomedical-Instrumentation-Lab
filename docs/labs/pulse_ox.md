# Pulse Oximetry Lab

## Purpose

This lab demonstrates multi-phase optical acquisition. Students observe raw photodiode readings during each LED phase and the corrected cycle values reconstructed from those phase measurements.

The default classroom configuration includes four physical analog channels:
- reflective photodiode raw output
- transmission photodiode raw output
- filtered reflective photodiode output
- filtered transmission photodiode output

Red versus IR is not determined by different analog pins. It is inferred from the phase in which the same channels are sampled.

## Acquisition summary

- Acquisition class: `PHASED_CYCLE`
- Default cycle rate: `100 cycles/s`
- Default phase rate: `400 phase samples/s`
- Default Arduino timestamp field: `t_us`
- Main packet types: `META`, `PHASE`, `CYCLE`, optional `STAT`, optional `ERR`

Phase sequence:
- `RED_ON`
- `DARK1`
- `IR_ON`
- `DARK2`

## Board and pin mapping

Default Arduino UNO R4 WiFi mapping:
- `A0 = Reflective photodiode raw output`
- `A1 = Transmission photodiode raw output`
- `A2 = Filtered reflective photodiode output`
- `A3 = Filtered transmission photodiode output`

LED control pins used by generated firmware:
- `D6 = RED LED control`
- `D5 = IR LED control`

Current repository note:
- the PulseOx classroom workflow uses GUI-generated firmware rather than a fixed committed reference sketch

## GUI setup

Recommended classroom path:
1. Connect the Arduino UNO R4 WiFi.
2. Start the student GUI with `python/run_student_acquisition_gui.py`.
3. In the lab dropdown, choose `Pulse Oximetry`.
4. Confirm the GUI loads the four fixed PulseOx channels on `A0` to `A3`.
5. Confirm students did not mix `PulseOx` with other presets in the same session.
6. Choose the save folder.
7. Compile and upload from the GUI.
8. Start acquisition.

Optional preset:
- `python/session_presets/pulse_ox.json`

## Firmware or profile to use

Use one of these:
- GUI lab profile: `Pulse Oximetry`
- GUI session preset: `python/session_presets/pulse_ox.json`

The GUI-generated firmware will:
- drive `D6` and `D5`
- sample `A0` to `A3` during every phase
- emit raw `PHASE` packets
- emit corrected `CYCLE` packets

## Expected output files

PulseOx sessions create one file:
- `<output>.csv`

Notes:
- `PHASE` rows in `<output>.csv` store raw phase samples for all four channels
- `CYCLE` rows in `<output>.csv` store corrected red and IR outputs by optical path and signal path
- `META`, `STAT`, `ERR`, and `PARSE_ERROR` rows are stored in the same session CSV
- current UNO R4 WiFi PulseOx firmware sets `analogReadResolution(14)` and reports `META,adc_resolution_bits,14`
- the session CSV uses readable PulseOx column labels derived from the configured channel names
- the live plot shows corrected `CYCLE` values, not every raw phase sample
- the live plot labels are derived from the four configured left-panel channels, with `RED corrected` and `IR corrected` suffixes

## Common troubleshooting

- PulseOx rows cannot be changed freely:
  This is expected. PulseOx uses fixed channel wiring on `A0` to `A3`.
- Red and IR seem mixed up:
  Check the LED wiring on `D6` and `D5`. Red versus IR comes from phase timing, not from separate analog pins.
- No corrected cycle plot appears:
  Confirm the session CSV contains both `PHASE` and `CYCLE` rows and inspect any `PARSE_ERROR` or `ERR` rows.
- Signals are noisy or close to zero:
  Check the photodiode board power, LED wiring, and optical alignment.
- Packet layout mismatch appears in logs:
  Recompile and upload from the GUI so the firmware and Python expectations match.

## Suggested screenshots

If you want to build classroom handouts later, place screenshots under `docs/screenshots/` with names such as:
- `pulse_ox_gui_setup.png`
- `pulse_ox_live_plot.png`
- `pulse_ox_board_wiring.jpg`
- `pulse_ox_sensor_alignment.jpg`
