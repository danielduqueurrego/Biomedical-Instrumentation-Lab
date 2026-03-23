# EMG Lab

## Purpose

This lab captures several stages of an EMG signal chain so students can compare the raw waveform with common conditioning steps.

The default classroom configuration includes:
- raw EMG
- rectified EMG
- enveloped EMG
- pressure

## Acquisition summary

- Acquisition class: `CONT_HIGH`
- Default sampling rate: `2000 samples/s`
- Default Arduino timestamp field: `t_us`
- Main packet types: `META`, `DATA`, optional `STAT`, optional `ERR`

## Board and analog pin mapping

Default Arduino UNO R4 WiFi mapping:
- `A0 = Raw EMG`
- `A1 = Rectified EMG`
- `A2 = Enveloped EMG`
- `A3 = Pressure`

Reference sketch:
- `firmware/cont_high/uno_r4_wifi/emg_four_channel_demo/emg_four_channel_demo.ino`

## GUI setup

Recommended classroom path:
1. Connect the Arduino UNO R4 WiFi.
2. Start the student GUI with `python/run_student_acquisition_gui.py`.
3. In the lab dropdown, choose `EMG`.
4. Confirm the GUI auto-detects the board and serial port.
5. Confirm the four EMG rows are loaded on `A0` to `A3`.
6. Choose the save folder.
7. Compile and upload from the GUI, then start acquisition.

Optional preset:
- `python/session_presets/emg.json`

## Firmware or profile to use

Use one of these:
- GUI lab profile: `EMG`
- GUI session preset: `python/session_presets/emg.json`
- committed reference sketch: `firmware/cont_high/uno_r4_wifi/emg_four_channel_demo`

For the normal student workflow, prefer the GUI lab profile or GUI preset.

## Expected output files

Continuous EMG sessions create one file:
- `<output>.csv`

Notes:
- `<output>.csv` stores `META`, `DATA`, and any error rows together
- EMG `DATA` rows store both host timestamps and Arduino `t_us`
- `PARSE_ERROR` and `ERR` rows should stay absent during a healthy session

## Common troubleshooting

- No board detected:
  Check the USB cable, then click `Refresh Ports`.
- Upload fails on Linux:
  Confirm the user has serial-port permission such as `dialout`.
- Plot looks frozen:
  Confirm acquisition actually started and check whether `<output>.csv` is growing with new `DATA` rows.
- Signals look swapped:
  Re-check the board wiring against `A0` to `A3`.
- Parsing errors appear:
  Open `<output>.csv` and check whether `PARSE_ERROR` rows contain unexpected serial text or malformed packets.

## Suggested screenshots

If you want to build classroom handouts later, place screenshots under `docs/screenshots/` with names such as:
- `emg_gui_setup.png`
- `emg_live_plot.png`
- `emg_board_wiring.jpg`
