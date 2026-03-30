# CONT_MED Firmware

Medium-rate continuous firmware for ECG, blood pressure, and analog demos.

## Included sketches
- `uno_r4_wifi/ecg_reference` (500 Hz)
- `uno_r4_wifi/blood_pressure_reference` (200 Hz)
- `uno_r4_wifi/three_channel_data_demo` (about 120 samples/s)

## Expected protocol behavior
- acquisition class: `CONT_MED`
- packet types: `META`, `DATA`
- timestamp field: `t_ms`

## Upload helpers
- ECG: `./tools/upload_cont_med_ecg_reference.sh`
- Blood pressure: `./tools/upload_cont_med_blood_pressure_reference.sh`
- Analog demo: `./tools/upload_cont_med_three_channel.sh`

(Windows `.bat` equivalents are also included in `tools/`.)

## Related docs
- [ECG guide](../../docs/labs/ecg.md)
- [Blood Pressure guide](../../docs/labs/blood_pressure.md)
- [Serial protocol](../../docs/serial_protocol.md)
