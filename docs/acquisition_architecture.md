# Acquisition architecture

This repository is organized by acquisition pattern first and by lab second.

## Supported acquisition classes

### `CONT_HIGH`
- Use for high-rate continuous waveforms such as EMG.
- Main packets: `META`, `DATA`, `STAT`, `ERR`
- Design goal: log every sample, plot a decimated rolling view, keep serial output simple.

### `CONT_MED`
- Use for medium-rate continuous waveforms such as ECG, Blood Pressure, and general analog streaming demos.
- Main packets: `META`, `DATA`, `STAT`, `ERR`
- Design goal: one timestamped CSV packet per sample with beginner-friendly live plotting.

### `PHASED_CYCLE`
- Use for timed phase sequences that reconstruct one cycle from several phase measurements, such as pulse oximetry.
- Main packets: `META`, `PHASE`, `CYCLE`, `STAT`, `ERR`
- Design goal: keep raw phase logs and reconstructed cycle logs in the same protocol family.

## Pattern-first repository layout

```text
firmware/
  cont_high/
    uno_r4_wifi/
      <lab_name>/
  cont_med/
    uno_r4_wifi/
      <lab_name>/
  phased_cycle/
    uno_r4_wifi/
      <lab_name>/

python/
  acquisition/
    architecture.py
    presets.py
    protocol.py
    serial_tools.py
    session_logging.py
    live_plot.py
  apps/
    <pattern_or_lab_app>.py
  run_<app>.py
  launch_<app>.sh
  launch_<app>.bat
```

## Lab mapping
- EMG: `CONT_HIGH`
- ECG: `CONT_MED`
- PulseOx: `PHASED_CYCLE`
- Blood Pressure: `CONT_MED`

## Blood pressure rule
- Blood pressure is modeled as `CONT_MED`.
- The pressure waveform and supporting channels are sent with `DATA`.
- Students manually inflate and deflate the cuff, so the project does not model separate procedure `EVENT` packets.

## PulseOx rule
- PulseOx is modeled as `PHASED_CYCLE`.
- The Arduino side logs one `PHASE` packet for each optical phase:
  - `RED_ON`
  - `DARK1`
  - `IR_ON`
  - `DARK2`
- After `DARK2`, the Arduino side reconstructs one corrected `CYCLE` packet for the configured signals.

## Current implementation status
1. Shared Python packet parsing and CSV logging are implemented for the continuous workflow.
2. `CONT_MED` is implemented end to end for the reference UNO R4 WiFi demo and the student GUI.
3. GUI-generated `PHASED_CYCLE` PulseOx firmware is implemented with raw `PHASE` logging and corrected `CYCLE` logging.
4. `CONT_HIGH` still uses the same shared GUI workflow, but more high-rate validation remains useful on real hardware.
