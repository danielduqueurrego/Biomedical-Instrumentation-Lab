# Example Session CSVs

> Small synthetic session files that show the current student-facing CSV format.

Use these files when you want to understand the logging structure before collecting real hardware data.

---

## 🚀 Start Here

Current example files:

- `emg_example_session.csv`
- `ecg_example_session.csv`
- `blood_pressure_example_session.csv`
- `pulse_ox_example_session.csv`

These are teaching artifacts, not live captures from a board.

---

## 📄 How To Read Them

Start with the `row_type` column:

- `META`: session setup, firmware, field layout, or hardware metadata
- `DATA`: continuous waveform samples for `CONT_HIGH` or `CONT_MED`
- `PHASE`: raw phase samples for `PHASED_CYCLE`
- `CYCLE`: corrected cycle values for `PHASED_CYCLE`
- `STAT`, `ERR`, `PARSE_ERROR`: status or error rows when present

Useful columns:

- `device_timestamp_field`: `t_ms` or `t_us`
- `device_timestamp`: the Arduino timestamp
- `cycle_idx`: present for `PHASE` and `CYCLE`
- `phase`: present for `PHASE`
- remaining signal columns: session-specific data columns

---

## 👩‍🎓 What Students Should Use First

- for ECG, EMG, and Blood Pressure:
  - filter to `row_type=DATA`
- for PulseOx:
  - start with `row_type=CYCLE`
  - use `row_type=PHASE` when checking the raw phase behavior

---

## 🔗 See Also

- [README.md](../../README.md)
- [Student setup](../../docs/student_setup.md)
- [Serial protocol](../../docs/serial_protocol.md)
