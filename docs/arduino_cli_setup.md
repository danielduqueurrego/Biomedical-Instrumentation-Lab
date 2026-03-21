# Arduino CLI setup

This project uses Arduino CLI to reduce the amount of clicking students need to do before running a lab.

For the full student workflow, including Conda setup and the Tkinter GUI, see `docs/student_setup.md`.

## Project requirement

All student systems need:
- Arduino CLI installed
- Arduino CLI available on `PATH`, or the environment variable `ARDUINO_CLI` set to the full executable path
- a data USB cable
- the Arduino UNO R4 WiFi board package: `arduino:renesas_uno`

This repository includes cross-platform helper scripts in `tools/` so students can run setup, compile, and upload commands without editing source files.

The Tkinter GUI also uses Arduino CLI board detection so the port can be filled automatically after the student selects a board.

## Recommended project workflow

From the repository root:

1. Install or update Arduino CLI.
2. Run the one-time board setup command:
   - macOS/Linux: `./tools/setup_arduino_cli.sh`
   - Windows: `tools\\setup_arduino_cli.bat`
3. Connect the UNO R4 WiFi by USB.
4. Upload the current `CONT_MED` reference sketch:
   - macOS/Linux: `./tools/upload_cont_med_three_channel.sh`
   - Windows: `tools\\upload_cont_med_three_channel.bat`

If auto-detection does not find the correct port, pass it explicitly:
- macOS/Linux: `./tools/upload_cont_med_three_channel.sh --port /dev/ttyACM0`
- Windows: `tools\\upload_cont_med_three_channel.bat --port COM3`

## Windows

Recommended requirements:
- install the latest Arduino CLI from the official Arduino CLI installation page
- make sure `arduino-cli.exe` is on `PATH`, or set `ARDUINO_CLI` to the executable path
- use Command Prompt or PowerShell to run the `.bat` helper scripts

Project notes:
- For UNO R4 WiFi uploads on Windows, keep Arduino CLI updated. Arduino support says the touch-reset upload fix is included in Arduino CLI `0.33.1` or later.
- If the board is not detected correctly after connecting it, reconnect it and try the upload again.

## macOS

Recommended requirements:
- install Arduino CLI with Homebrew, or use the official install script/download
- make sure `arduino-cli` is on `PATH`
- run the `.sh` helper scripts from Terminal

Project notes:
- `brew install arduino-cli` is the simplest path for students who already use Homebrew.
- If Arduino CLI was installed manually, add the install folder to `PATH` before using the helper scripts.

## Linux

Recommended requirements:
- install Arduino CLI with Homebrew, the official install script, or the official download
- make sure `arduino-cli` is on `PATH`
- run the `.sh` helper scripts from Terminal

Project notes:
- If uploads fail with permission errors, follow Arduino's Linux serial-port guidance:
  - add the user to the `dialout` group if your system uses it
  - if needed, add the user to the group that owns the device node
  - if uploads fail after reset, check the udev rules guidance from Arduino

## Commands used by this project

The helper tool wraps these Arduino CLI operations:
- `arduino-cli core update-index`
- `arduino-cli core install arduino:renesas_uno`
- `arduino-cli compile --fqbn arduino:renesas_uno:unor4wifi <sketch-folder>`
- `arduino-cli upload --fqbn arduino:renesas_uno:unor4wifi --port <port> <sketch-folder>`

The current reference sketch is:
- `firmware/cont_med/uno_r4_wifi/three_channel_data_demo`

## If Arduino CLI is installed but not found

If the helper scripts report that Arduino CLI is missing, do one of these:
- add Arduino CLI to your system `PATH`
- set `ARDUINO_CLI` to the executable path
- pass `--arduino-cli /full/path/to/arduino-cli` to `tools/arduino_cli.py`

## Official references

- Arduino CLI installation: https://docs.arduino.cc/arduino-cli/installation
- Arduino CLI getting started: https://docs.arduino.cc/arduino-cli/getting-started/
- Linux port access help: https://support.arduino.cc/hc/en-us/articles/360016495679-Fix-port-access-on-Linux
- UNO R4 WiFi Windows upload note: https://support.arduino.cc/hc/en-us/articles/9398559565340-Touch-reset-fails-for-UNO-R4-WiFi-on-Windows-Arduino-CLI-0-33-0-or-earlier
- UNO R4 WiFi connectivity firmware help: https://support.arduino.cc/hc/en-us/articles/9670986058780-Update-the-connectivity-module-firmware-on-UNO-R4-WiFi
