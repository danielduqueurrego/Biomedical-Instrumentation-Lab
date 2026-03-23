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

Example:
- `EMG` at `2000` samples/s
- `Blood Pressure` at `200` samples/s

The generated sketch uses:
- `2000` samples/s
- continuous `DATA` packets

## PulseOx phased-cycle workflow

If the selected signals use the `PulseOx` preset, the generated sketch switches to `PHASED_CYCLE` mode.

Rules:
- all active signals must be `PulseOx` signals
- each active signal must declare a `PulseOx role` of `RED` or `IR`

The generated sketch then:
- drives `D6` for the red LED
- drives `D5` for the IR LED
- steps through the phase sequence:
  - `RED_ON`
  - `DARK1`
  - `IR_ON`
  - `DARK2`
- emits one raw `PHASE` packet per phase
- emits one corrected `CYCLE` packet after `DARK2`

For PulseOx, the GUI:
- logs raw phase packets to `<output>_phase.csv`
- logs corrected cycle packets to `<output>_cycle.csv`
- plots the corrected `CYCLE` values live

The generated sketch also emits metadata such as:
- `META,phase_fields,...`
- `META,cycle_fields,...`
- `META,pulseox_signal_roles,...`
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
