# `CONT_MED` firmware

Place medium-rate continuous waveform sketches here.

Typical labs:
- ECG
- general analog streaming demos

Expected packet mix:
- `META`
- `DATA`
- optional `STAT`
- optional `ERR`

Current student helper workflow:
- one-time setup with `tools/setup_arduino_cli.sh` or `tools/setup_arduino_cli.bat`
- compile/upload with `tools/upload_cont_med_three_channel.sh` or `tools/upload_cont_med_three_channel.bat`
