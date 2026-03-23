# CONT_HIGH UNO R4 WiFi EMG high-rate reference

This sketch is a fixed reference for high-rate EMG demonstration on Arduino UNO R4 WiFi.
It emits shared-protocol `META` and `DATA` packets at a 1 kHz target rate.

Packet fields:
- `t_us`: Arduino `micros()` timestamp
- `EMG_A0`: analog sample from `A0`
- `EMG_A1`: analog sample from `A1`

From repository root, compile and upload with:
- macOS/Linux: `./tools/upload_cont_high_emg_reference.sh`
- Windows: `tools\\upload_cont_high_emg_reference.bat`

If auto-detect cannot find the board port:
- `python tools/arduino_cli.py upload-cont-high-emg --port /dev/ttyACM0`
- `python tools/arduino_cli.py upload-cont-high-emg --port COM3`
