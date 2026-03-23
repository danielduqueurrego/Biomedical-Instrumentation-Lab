# Blood Pressure Lab

## Purpose

This lab records the pressure waveform while students manually inflate and deflate the cuff. It also keeps the additional photodiode channels that are currently part of the standard lab profile.

The default classroom configuration includes:
- raw pressure
- filtered pressure
- red PD
- IR PD

## Acquisition summary

- Acquisition class: `CONT_MED`
- Default sampling rate: `200 samples/s`
- Default Arduino timestamp field: `t_ms`
- Main packet types: `META`, `DATA`, optional `STAT`, optional `ERR`

Important classroom note:
- blood pressure is treated as a continuous waveform lab
- students manually control cuff inflation and deflation
- the project does not emit procedure-stage events for this lab

## Board and analog pin mapping

Default Arduino UNO R4 WiFi mapping:
- `A0 = Raw Pressure`
- `A1 = Filtered Pressure`
- `A2 = Red PD`
- `A3 = IR PD`

The standard Blood Pressure classroom workflow uses GUI-generated firmware rather than a dedicated committed blood-pressure sketch.

## GUI setup

Recommended classroom path:
1. Connect the Arduino UNO R4 WiFi.
2. Start the student GUI with `python/run_student_acquisition_gui.py`.
3. In the lab dropdown, choose `Blood Pressure`.
4. Confirm the GUI loads the four lab channels on `A0` to `A3`.
5. Choose the save folder.
6. Compile and upload from the GUI.
7. Start acquisition before the cuff procedure begins.

Optional preset:
- `python/session_presets/blood_pressure.json`

## Firmware or profile to use

Use one of these:
- GUI lab profile: `Blood Pressure`
- GUI session preset: `python/session_presets/blood_pressure.json`

The GUI will generate the Arduino code from the current signal selection and the default Blood Pressure rate.

## Expected output files

Blood Pressure sessions create:
- `<output>_data.csv`
- `<output>_metadata.csv`
- `<output>_errors.log`

Notes:
- `<output>_data.csv` stores both host timestamps and Arduino `t_ms`
- the output stays on the continuous `DATA` workflow during manual cuff inflation and deflation

## Common troubleshooting

- Pressure trace is clipped:
  Check the sensor scaling and confirm the expected pressure channel is on `A0`.
- Filtered pressure looks identical to raw pressure:
  Re-check the analog conditioning path feeding `A1`.
- Students started too early or too late:
  Note the timing in bench notes and repeat the capture rather than editing timestamps by hand.
- Serial drops during the procedure:
  Inspect `<output>_errors.log` and repeat the session with a shorter USB cable if needed.
- Board detection fails:
  Confirm the Arduino UNO R4 WiFi is still present in Arduino CLI and click `Refresh Ports`.

## Suggested screenshots

If you want to build classroom handouts later, place screenshots under `docs/screenshots/` with names such as:
- `blood_pressure_gui_setup.png`
- `blood_pressure_live_plot.png`
- `blood_pressure_board_wiring.jpg`
