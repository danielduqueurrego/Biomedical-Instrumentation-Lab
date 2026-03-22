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

Current UNO R4 WiFi reference behavior:
- stream `A0` to `A5` at about 120 Hz
- let the Python GUI choose which subset of those six analog inputs is active

GUI-generated behavior:
- compile and upload a temporary Arduino sketch from the current GUI signal selection
- use only the selected analog ports
- set the sample rate to the highest selected preset rate
