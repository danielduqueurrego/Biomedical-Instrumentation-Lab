# Acquisition architecture

This repository is organized by acquisition pattern first and by lab second.

## Supported acquisition classes

### `CONT_HIGH`
- Use for high-rate continuous waveforms such as EMG.
- Main packets: `META`, `DATA`, `STAT`, `ERR`
- Design goal: log every sample, plot a decimated rolling view, keep serial output simple.

### `CONT_MED`
- Use for medium-rate continuous waveforms such as ECG and general analog streaming demos.
- Main packets: `META`, `DATA`, `STAT`, `ERR`
- Design goal: one timestamped CSV packet per sample with beginner-friendly live plotting.

### `PHASED_CYCLE`
- Use for timed phase sequences that reconstruct one cycle from several phase measurements, such as pulse oximetry.
- Main packets: `META`, `PHASE`, `CYCLE`, `STAT`, `ERR`
- Design goal: keep raw phase logs and reconstructed cycle logs in the same protocol family.

### `PROC_CONT`
- Use for continuous acquisitions that also need procedure or stage events, such as blood pressure.
- Main packets: `META`, `DATA`, `EVENT`, `STAT`, `ERR`
- Design goal: continuous waveform logging plus explicit stage markers for later analysis.

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
  proc_cont/
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
- Blood Pressure: `PROC_CONT`

## Blood pressure rule
- Blood pressure is modeled as `PROC_CONT`.
- The pressure waveform is sent with `DATA`.
- Procedure changes are sent with `EVENT`.
- Recommended default stage names are `BASELINE`, `INFLATE`, `HOLD`, `DEFLATE`, `COMPLETE`.

## First implementation order
1. Finish the shared Python packet parser and CSV logger around `META`, `DATA`, and `ERR`.
2. Stabilize one `CONT_MED` reference app because it is the easiest end-to-end student workflow.
3. Add `CONT_HIGH` support with the same logging stack but faster plot decimation and buffering.
4. Add `PHASED_CYCLE` support for PulseOx using shared metadata and cycle reconstruction helpers.
5. Add `PROC_CONT` support for Blood Pressure with stage-event handling and summary statistics.
