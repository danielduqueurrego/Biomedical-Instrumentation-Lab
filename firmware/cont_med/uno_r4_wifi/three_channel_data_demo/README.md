# CONT_MED three-channel demo

This sketch is the current Arduino CLI reference demo for the repository.

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
