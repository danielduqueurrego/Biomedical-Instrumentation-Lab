# Hardware Validation Framework

Use this section when a board, lab station, or firmware change needs a quick bench checkout.

The goal is to keep validation simple and repeatable for instructors, TAs, and students.

## What should be recorded

Each validation session should record at least:
- target sample rate or cycle rate
- achieved rate measured from the saved CSV data
- serial stability during the run
- packet loss or malformed packets
- plot responsiveness during live viewing
- bench notes, including wiring changes or observed issues

## Validation workflow

1. Choose the correct lab guide from `docs/labs/`.
2. Load the matching GUI lab profile or session preset.
3. Compile and upload firmware from the GUI.
4. Run a short acquisition, usually 30 to 60 seconds.
5. Save the output files and complete the validation checklist.
6. Keep screenshots or wiring photos if they help explain a failure or a good known setup.

## How to estimate achieved rate

### Continuous labs

Use `<output>_data.csv`.

One simple estimate is:
- `achieved_rate_hz = (sample_count - 1) / ((last_device_time - first_device_time) / time_scale)`

Use:
- `time_scale = 1000` for `t_ms`
- `time_scale = 1000000` for `t_us`

### PulseOx

Use `<output>_cycle.csv` to estimate achieved cycle rate and `<output>_phase.csv` to estimate achieved phase rate.

One simple estimate is:
- `achieved_cycle_rate_hz = (cycle_count - 1) / ((last_device_time_us - first_device_time_us) / 1000000)`
- `achieved_phase_rate_hz = (phase_count - 1) / ((last_device_time_us - first_device_time_us) / 1000000)`

## How to check packet quality

Use these saved files:
- `<output>_errors.log`
- `<output>_metadata.csv`

Healthy signs:
- the error log is empty or only contains explained test interruptions
- the metadata matches the expected field layout for the lab
- the GUI plot updates smoothly enough to follow the signal during class use

Warning signs:
- repeated malformed-packet lines
- metadata showing the wrong field set
- obvious serial disconnects or resets during the run
- a live plot that updates so slowly that students cannot follow the experiment

## Reusable checklist

Use:
- [Hardware validation checklist template](./hardware_validation_checklist_template.md)

## Screenshot placeholders

If screenshots help, place them under:
- `docs/screenshots/`

Suggested files:
- `validation_emg_plot.png`
- `validation_ecg_plot.png`
- `validation_pulse_ox_plot.png`
- `validation_blood_pressure_plot.png`
- `validation_board_wiring.jpg`
