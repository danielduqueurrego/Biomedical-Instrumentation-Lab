# `CONT_HIGH` firmware

Place high-rate continuous waveform sketches here.

Typical labs:
- EMG

Expected packet mix:
- `META`
- `DATA`
- optional `STAT`
- optional `ERR`

Committed UNO R4 WiFi sketches:
- `uno_r4_wifi/emg_high_rate_reference`
- `uno_r4_wifi/emg_four_channel_demo`

Current reference behavior:
- `emg_high_rate_reference` is a simple 1 kHz two-channel upload helper path
- `emg_four_channel_demo` is the manifest-aligned four-channel EMG example at `2000` samples/s
- both sketches follow the shared `CONT_HIGH` timing rule and emit `t_us`

Student helper workflow:
- one-time setup with `tools/setup_arduino_cli.sh` or `tools/setup_arduino_cli.bat`
- compile/upload the simple two-channel reference with `tools/upload_cont_high_emg_reference.sh` or `tools/upload_cont_high_emg_reference.bat`

Expected timing rule:
- use `t_us` timestamps for shared `CONT_HIGH` waveform packets
