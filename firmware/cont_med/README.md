# `CONT_MED` Firmware

> Committed medium-rate continuous sketches for ECG, Blood Pressure, and general analog demos.

Use this folder when you need a known committed `CONT_MED` sketch instead of the GUI-generated firmware path.

---

## 🚀 Start Here

Typical labs:

- ECG
- Blood Pressure
- general analog streaming demos

Current committed UNO R4 WiFi reference paths:

- `uno_r4_wifi/ecg_reference` — named ECG sketch at 500 Hz (A0=Raw ECG, A1=Amplified ECG, A2=Comparator)
- `uno_r4_wifi/blood_pressure_reference` — named Blood Pressure sketch at 200 Hz (A0=Pressure Waveform)
- `uno_r4_wifi/three_channel_data_demo` — generic six-channel analog-bank demo at 120 Hz

---

## 🧠 What `CONT_MED` Means In This Repo

Current expectations:

- use `META` and `DATA`
- log every sample
- use `t_ms`
- keep live plotting readable during class

Current GUI-generated behavior:

- emit only the selected analog ports
- use the highest selected preset rate
- keep Blood Pressure on the same continuous `DATA` workflow

---

## 🚀 Quick Use

- one-time setup:
  - `./tools/setup_arduino_cli.sh`
  - `tools\setup_arduino_cli.bat`
- ECG reference upload:
  - `./tools/upload_cont_med_ecg_reference.sh`
  - `tools\upload_cont_med_ecg_reference.bat`
- Blood Pressure reference upload:
  - `./tools/upload_cont_med_blood_pressure_reference.sh`
  - `tools\upload_cont_med_blood_pressure_reference.bat`
- generic analog-bank demo upload:
  - `./tools/upload_cont_med_three_channel.sh`
  - `tools\upload_cont_med_three_channel.bat`

---

## 🔗 See Also

- [Sampling strategy](../../docs/sampling_strategy.md)
- [Serial protocol](../../docs/serial_protocol.md)
- [ECG lab guide](../../docs/labs/ecg.md)
- [Blood Pressure lab guide](../../docs/labs/blood_pressure.md)
