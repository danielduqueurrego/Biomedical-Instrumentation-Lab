# `CONT_HIGH` firmware

Place high-rate continuous waveform sketches here.

Typical labs:
- EMG

Expected packet mix:
- `META`
- `DATA`
- optional `STAT`
- optional `ERR`

Current UNO R4 WiFi reference behavior:
- `firmware/cont_high/uno_r4_wifi/emg_high_rate_reference/emg_high_rate_reference.ino`
- streams `EMG_A0` and `EMG_A1` at a 1 kHz target for EMG demonstration
- emits startup metadata with `acq_class=CONT_HIGH`, `rate_hz=1000`, and `fields=t_ms,EMG_A0,EMG_A1`

Student helper workflow:
- one-time setup with `tools/setup_arduino_cli.sh` or `tools/setup_arduino_cli.bat`
- compile/upload with `tools/upload_cont_high_emg_reference.sh` or `tools/upload_cont_high_emg_reference.bat`
