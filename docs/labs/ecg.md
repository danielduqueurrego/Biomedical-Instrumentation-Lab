# ECG Lab

## Purpose

This lab lets students compare a raw ECG pickup with a conditioned waveform and a thresholded comparator output.

The default classroom configuration includes:
- raw ECG
- amplified ECG
- comparator output

## Acquisition summary

- Acquisition class: `CONT_MED`
- Default sampling rate: `500 samples/s`
- Default Arduino timestamp field: `t_ms`
- Main packet types: `META`, `DATA`, optional `STAT`, optional `ERR`

## Board and analog pin mapping

Default Arduino UNO R4 WiFi mapping:
- `A0 = Raw ECG`
- `A1 = Amplified ECG`
- `A2 = Comparator Output`

The standard ECG classroom workflow uses GUI-generated firmware rather than a dedicated committed ECG sketch.

## GUI setup

Recommended classroom path:
1. Connect the Arduino UNO R4 WiFi.
2. Start the student GUI with `python/run_student_acquisition_gui.py`.
3. In the lab dropdown, choose `ECG`.
4. Confirm the GUI loads the three ECG signals on `A0` to `A2`.
5. Choose the save folder.
6. Compile and upload from the GUI.
7. Start acquisition.

Optional preset:
- `python/session_presets/ecg.json`

## Firmware or profile to use

Use one of these:
- GUI lab profile: `ECG`
- GUI session preset: `python/session_presets/ecg.json`

The GUI will generate the Arduino code from the current signal selection and the default ECG rate.

## Expected output files

Continuous ECG sessions create:
- `<output>_data.csv`
- `<output>_metadata.csv`
- `<output>_errors.log`

Notes:
- `<output>_data.csv` stores both host timestamps and Arduino `t_ms`
- the GUI does not create PulseOx-style `_phase.csv` or `_cycle.csv` files for ECG

## Common troubleshooting

- Port field is empty:
  Click `Refresh Ports` and confirm the board appears in Arduino CLI.
- Comparator output looks flat:
  Verify the comparator channel is actually wired to `A2`.
- Sampling looks slower than expected:
  Check `<output>_metadata.csv` for the declared `CONT_MED` rate and use the hardware validation checklist.
- File overwrite warning appears:
  Stop acquisition and use the auto-refreshed timestamped output basename.
- Parse errors appear:
  Inspect `<output>_errors.log` for malformed lines or unexpected text.

## Suggested screenshots

If you want to build classroom handouts later, place screenshots under `docs/screenshots/` with names such as:
- `ecg_gui_setup.png`
- `ecg_live_plot.png`
- `ecg_board_wiring.jpg`
