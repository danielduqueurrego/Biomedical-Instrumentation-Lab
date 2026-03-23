# Example session CSVs

These files are small synthetic examples that match the current student-facing session CSV format.

Use them to learn the logging structure before running hardware:
- `emg_example_session.csv`
- `ecg_example_session.csv`
- `blood_pressure_example_session.csv`
- `pulse_ox_example_session.csv`

## How to read them

Start with the `row_type` column:
- `META`: session setup, firmware, field layout, or hardware metadata
- `DATA`: continuous waveform samples for `CONT_HIGH` or `CONT_MED`
- `PHASE`: raw phase samples for `PHASED_CYCLE`
- `CYCLE`: reconstructed corrected cycle values for `PHASED_CYCLE`
- `STAT`, `ERR`, or `PARSE_ERROR`: status or error rows when present

Useful columns:
- `device_timestamp_field`: `t_ms` or `t_us`
- `device_timestamp`: the Arduino timestamp value
- `cycle_idx`: present for `PHASE` and `CYCLE`
- `phase`: present for `PHASE`
- remaining signal columns: the student-facing data columns for that session

## What students should use first

- For ECG, EMG, and Blood Pressure:
  filter to `row_type=DATA`
- For PulseOx:
  use `row_type=CYCLE` first for the corrected plotted values
  use `row_type=PHASE` when checking the raw optical phase behavior

These files are examples only. They are not captured from a live board.
