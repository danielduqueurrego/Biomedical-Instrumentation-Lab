# Generated Firmware Workflow

This document describes what the student GUI does when it compiles or uploads Arduino firmware.

## Why generated firmware is used

The student GUI does not always compile the fixed reference sketch directly.
Instead, it can generate a temporary Arduino UNO R4 WiFi sketch from the current GUI signal selection.

This keeps the student workflow simple:
- choose a lab profile or custom signal setup
- compile or upload from the GUI
- review the exact Arduino code that was used

## What the generated sketch includes

For the current GUI signal selection, the generated sketch:
- emits only the selected analog ports
- uses the highest default rate among the selected signal presets
- writes matching `META,rate_hz,...` and `META,fields,...` packets
- saves a timestamped copy of the generated Arduino code for review

## Example rate rule

If the selected signals include:
- `EMG` at `2000` samples/s
- `Blood Pressure` at `200` samples/s

the generated sketch uses:
- `2000` samples/s

## Pulse oximetry LED handling

If any selected signal uses the `PulseOx` preset, the generated sketch also adds LED phase control:
- `D6` controls the red LED
- `D5` controls the IR LED
- phase sequence: `RED_ON`, `DARK1`, `IR_ON`, `DARK2`

The generated sketch emits metadata such as:
- `META,pulseox_led_pins,IR_D5,RED_D6`
- `META,pulseox_phase_sequence,RED_ON,DARK1,IR_ON,DARK2`

Current limitation:
- the GUI still logs `DATA` packets for the selected analog ports
- this does not yet replace the full future `PHASED_CYCLE` PulseOx implementation

## Saved Arduino code copies

After each successful compile, the project saves a timestamped Arduino code copy under:
- `data/arduino_code_snapshots/arduino_code_YYYY_MM_DD_HH_MM_SS.ino`

This lets instructors and students inspect the exact Arduino code that was compiled.

## Generated sketch location

The temporary generated sketch folders are stored under:
- `data/generated_arduino_sketches/`

These are runtime artifacts and are not intended to be committed.
