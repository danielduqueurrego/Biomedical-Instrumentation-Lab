# Arduino CLI Setup

> Arduino CLI setup guide for the repo’s student workflow, reference sketches, and GUI upload path.

Use this document when you need to prepare Arduino CLI or troubleshoot firmware compile and upload behavior. If you want the full student path from first install to first plot, start with [student_setup.md](./student_setup.md).

---

## Start Here

This project uses Arduino CLI so students can compile and upload firmware without working directly inside the Arduino IDE.

Every student system needs:

- Arduino CLI installed
- Arduino CLI available on `PATH`, or `ARDUINO_CLI` set to the executable path
- a USB data cable
- the UNO R4 WiFi board core: `arduino:renesas_uno`

The repo includes helper scripts in `tools/` so the normal classroom flow is one command per step instead of a manual Arduino CLI session.

---

## Quick Setup

From the repository root:

1. Install or update Arduino CLI.
2. Run the one-time setup script:
   - macOS/Linux: `./tools/setup_arduino_cli.sh`
   - Windows: `tools\setup_arduino_cli.bat`
3. Connect the Arduino UNO R4 WiFi by USB.
4. Confirm board detection:
   - `python tools/arduino_cli.py board-list`

If you are using the student GUI, this is enough. The GUI can then detect the board, compile firmware, and upload it from the current lab configuration.

---

## Quick Reference Commands

### One-time setup

- macOS/Linux: `./tools/setup_arduino_cli.sh`
- Windows: `tools\setup_arduino_cli.bat`

### Board detection

- `python tools/arduino_cli.py board-list`

### Compile current `CONT_MED` reference sketch

- `python tools/arduino_cli.py compile-demo`

### Upload current `CONT_MED` reference sketch

- macOS/Linux: `./tools/upload_cont_med_three_channel.sh`
- Windows: `tools\upload_cont_med_three_channel.bat`

### Upload current `CONT_HIGH` EMG reference sketch

- macOS/Linux: `./tools/upload_cont_high_emg_reference.sh`
- Windows: `tools\upload_cont_high_emg_reference.bat`

---

## What The GUI Does With Arduino CLI

The student GUI uses Arduino CLI for:

- board detection
- compile-only checks
- firmware upload

Current GUI behavior:

- if one supported board is connected, the GUI usually fills the board and port automatically
- if no supported board is detected, upload fails fast with a readable message
- compile and upload commands use timeouts so a missing or busy board does not look like the app froze
- every successful compile saves a copy of the exact Arduino code used under `data/arduino_code_snapshots/`

---

## Reference Sketches And Generated Firmware

### Committed reference sketches

The repo currently includes these main committed sketches:

- `firmware/cont_med/uno_r4_wifi/three_channel_data_demo`
- `firmware/cont_high/uno_r4_wifi/emg_high_rate_reference`
- `firmware/cont_high/uno_r4_wifi/emg_four_channel_demo`
- `firmware/phased_cycle/uno_r4_wifi/pulse_ox_reference`

### GUI-generated firmware

When students compile or upload from the GUI, the repo usually generates a temporary sketch from the current signal selection.

Current generated behavior:

- only the selected analog ports are emitted
- the sample rate is the highest selected preset rate
- `CONT_HIGH` emits `t_us`
- `CONT_MED` emits `t_ms`
- generated firmware sets `analogReadResolution(14)` on the UNO R4 WiFi
- PulseOx switches to `PHASED_CYCLE` mode and uses the fixed PulseOx analog map

For details, see [generated_firmware_workflow.md](./generated_firmware_workflow.md).

---

## Current Board Core Assumption

This repo currently targets:

- board family: `arduino:renesas_uno`
- main board used in class: `arduino:renesas_uno:unor4wifi`

If that changes in the future, update:

- the Arduino CLI helper scripts
- the GUI defaults
- CI compile smoke tests
- the firmware READMEs

---

## Troubleshooting

### Arduino CLI is not found

- make sure `arduino-cli` is on `PATH`
- or set `ARDUINO_CLI` to the full executable path
- rerun `python python/system_check.py`

### The board is connected but upload fails

- confirm the port shown by `python tools/arduino_cli.py board-list`
- close any serial monitor or other program that may be holding the port
- on Linux, confirm the user has serial-port access

### Upload seems to hang

Current GUI and helper commands use timeouts. If a timeout occurs:

- reconnect the board
- rerun the board-list command
- check that the selected port still matches the detected board

---

## See Also

- [README.md](../README.md)
- [student_setup.md](./student_setup.md)
- [generated_firmware_workflow.md](./generated_firmware_workflow.md)
- [serial_protocol.md](./serial_protocol.md)
