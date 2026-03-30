# Example Session CSV Files

Small synthetic files that show the expected CSV structure.

## Included examples
- `emg_example_session.csv`
- `ecg_example_session.csv`
- `blood_pressure_example_session.csv`
- `pulse_ox_example_session.csv`

## Row types
- `META` → setup and metadata
- `DATA` → continuous samples (`CONT_HIGH`/`CONT_MED`)
- `PHASE` → phase-level samples (`PHASED_CYCLE`)
- `CYCLE` → corrected pulse-ox cycle values
- `STAT`, `ERR`, `PARSE_ERROR` → status and errors

## Teaching tip
- For EMG/ECG/BP: start by filtering `row_type=DATA`
- For PulseOx: start with `row_type=CYCLE`

## Related docs
- [Main README](../../README.md)
- [Serial protocol](../../docs/serial_protocol.md)
