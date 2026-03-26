# `CONT_MED` UNO R4 Analog-Bank Demo

> Fixed reference sketch that streams the six standard UNO R4 WiFi analog inputs for simple classroom demos and smoke tests.

Use this sketch when you want a simple committed reference upload instead of a GUI-generated sketch.

---

## Quick Reference

| Item | Current value |
| --- | --- |
| Acquisition class | `CONT_MED` |
| Approximate rate | `120 samples/s` |
| Timestamp field | `t_ms` |
| Analog inputs | `A0` to `A5` |
| ADC setting | `analogReadResolution(14)` |

---

## What It Does

This sketch:

- streams `A0` to `A5`
- uses the shared protocol
- serves as the basic Arduino CLI reference demo

The student GUI can then choose a subset of those six inputs and assign student-friendly signal names and presets.

When students compile or upload from the GUI, the project generates a temporary sketch that uses the selected ports and the highest selected preset rate instead of this fixed `120 Hz` reference file.

---

## Quick Use

From the repository root:

- compile only:
  - `python tools/arduino_cli.py compile-demo`
- compile and upload:
  - macOS/Linux: `./tools/upload_cont_med_three_channel.sh`
  - Windows: `tools\upload_cont_med_three_channel.bat`

If the port is not detected automatically:

- `python tools/arduino_cli.py upload-demo --port /dev/ttyACM0`
- `python tools/arduino_cli.py upload-demo --port COM3`

---

## See Also

- [CONT_MED firmware overview](../../README.md)
- [Student setup](../../../../docs/student_setup.md)
