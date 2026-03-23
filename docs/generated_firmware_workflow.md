# Generated Firmware Workflow

This document describes what the student GUI does when it compiles or uploads Arduino firmware.

## Why generated firmware is used

The student GUI does not always compile the fixed reference sketch directly.
Instead, it generates a temporary Arduino UNO R4 WiFi sketch from the current GUI signal selection.

This keeps the student workflow simple:
- choose a lab profile or custom signal setup
- compile or upload from the GUI
- review the exact Arduino code that was used

## Continuous workflow

If the selected signals do not use the `PulseOx` preset, the generated sketch:
- uses the highest default rate among the selected signal presets
- emits only the selected analog ports
- sends `META,fields,...` and `DATA,...` packets
- behaves as `CONT_HIGH` or `CONT_MED` depending on the selected rate
- uses `t_us` timestamps for `CONT_HIGH`
- uses `t_ms` timestamps for `CONT_MED`

Example:
- `EMG` at `2000` samples/s
- `Blood Pressure` at `200` samples/s

The generated sketch uses:
- `2000` samples/s
- continuous `DATA` packets
- `t_us` timing because the resulting acquisition class is `CONT_HIGH`

## PulseOx phased-cycle workflow

If the selected signals use the `PulseOx` preset, the generated sketch switches to `PHASED_CYCLE` mode.

Rules:
- all active signals must be `PulseOx` signals
- PulseOx uses a fixed UNO R4 WiFi analog mapping:
  - `A0 = reflective_raw`
  - `A1 = transmission_raw`
  - `A2 = reflective_filtered`
  - `A3 = transmission_filtered`

The generated sketch then:
- drives `D6` for the red LED
- drives `D5` for the IR LED
- steps through the phase sequence:
  - `RED_ON`
  - `DARK1`
  - `IR_ON`
  - `DARK2`
- samples all four PulseOx analog channels during every phase
- emits one raw `PHASE` packet per phase with the fields:
  - `reflective_raw`
  - `transmission_raw`
  - `reflective_filtered`
  - `transmission_filtered`
- emits one corrected `CYCLE` packet after `DARK2` with the fields:
  - `reflective_raw_red_corr`
  - `reflective_raw_ir_corr`
  - `transmission_raw_red_corr`
  - `transmission_raw_ir_corr`
  - `reflective_filtered_red_corr`
  - `reflective_filtered_ir_corr`
  - `transmission_filtered_red_corr`
  - `transmission_filtered_ir_corr`

Red and IR are not separate analog outputs. They are inferred from the active LED phase.

For PulseOx, the GUI:
- logs raw phase packets to `<output>_phase.csv`
- logs corrected cycle packets to `<output>_cycle.csv`
- plots the corrected `CYCLE` values live

The generated sketch also emits metadata such as:
- `META,phase_fields,...`
- `META,cycle_fields,...`
- `META,pulseox_analog_map,...`
- `META,pulseox_led_pins,IR_D5,RED_D6`
- `META,pulseox_phase_sequence,RED_ON,DARK1,IR_ON,DARK2`

## Blood pressure note

Blood pressure now uses the continuous workflow.

- The project does not emit procedure stage packets for blood pressure.
- Students manually inflate and deflate the cuff while the waveform is logged continuously.

## Saved Arduino code copies

After each successful compile, the project saves a timestamped Arduino code copy under:
- `data/arduino_code_snapshots/arduino_code_YYYY_MM_DD_HH_MM_SS.ino`

This lets instructors and students inspect the exact Arduino code that was compiled.

## Generated sketch location

The temporary generated sketch folders are stored under:
- `data/generated_arduino_sketches/`

These are runtime artifacts and are not intended to be committed.

## Migration note

- High-rate continuous generated firmware now emits `META,fields,t_us,...` and `DATA,t_us,...`.
- Medium-rate continuous generated firmware is unchanged and still emits `t_ms`.
