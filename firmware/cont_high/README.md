# CONT_HIGH Firmware

High-rate continuous acquisition firmware (typically EMG).

## Included sketches
- `uno_r4_wifi/emg_high_rate_reference` (1000 Hz, 2 channels)
- `uno_r4_wifi/emg_four_channel_demo` (2000 samples/s, 4 channels)

## Expected protocol behavior
- acquisition class: `CONT_HIGH`
- packet types: `META`, `DATA`
- timestamp field: `t_us`

## Quick upload helpers
- Linux/macOS: `./tools/upload_cont_high_emg_reference.sh`
- Windows: `tools\upload_cont_high_emg_reference.bat`

## Related docs
- [EMG lab guide](../../docs/labs/emg.md)
- [Serial protocol](../../docs/serial_protocol.md)
