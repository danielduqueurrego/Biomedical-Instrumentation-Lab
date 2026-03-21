# CONT_MED UNO R4 analog-bank demo

This sketch is the current Arduino CLI reference demo for the repository.
It streams the six standard Arduino UNO R4 WiFi analog inputs `A0` to `A5` at about 120 Hz.
The student GUI can then choose any subset of those six inputs and assign each one a student-friendly signal name and preset.

## One-time setup

From the repository root:
- macOS/Linux: `./tools/setup_arduino_cli.sh`
- Windows: `tools\\setup_arduino_cli.bat`

## Compile only

From the repository root:
- `python tools/arduino_cli.py compile-demo`

## Compile and upload

From the repository root:
- macOS/Linux: `./tools/upload_cont_med_three_channel.sh`
- Windows: `tools\\upload_cont_med_three_channel.bat`

If the port is not detected automatically:
- `python tools/arduino_cli.py upload-demo --port /dev/ttyACM0`
- `python tools/arduino_cli.py upload-demo --port COM3`
