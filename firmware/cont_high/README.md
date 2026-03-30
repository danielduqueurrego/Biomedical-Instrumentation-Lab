# `CONT_HIGH` Firmware

> Committed high-rate continuous sketches, mainly for EMG-style waveform capture.

Use this folder when you need a known committed `CONT_HIGH` sketch instead of the GUI-generated firmware path.

---

## 🚀 Start Here

Current committed UNO R4 WiFi sketches:

- `uno_r4_wifi/emg_high_rate_reference`
- `uno_r4_wifi/emg_four_channel_demo`

Both follow the shared `CONT_HIGH` timing rule and emit `t_us`.

---

## 🧠 What `CONT_HIGH` Means In This Repo

Current expectations:

- use `META` and `DATA` packets
- log every sample
- use `t_us` for waveform timestamps
- keep the Arduino code simple enough for students to inspect

Typical classroom use:

- EMG

---

## 🧩 Current Sketch Roles

- `emg_high_rate_reference`: simple two-channel upload helper at `1 kHz`
- `emg_four_channel_demo`: manifest-aligned four-channel EMG example at `2000 samples/s`

---

## 🚀 Quick Use

- one-time setup:
  - `./tools/setup_arduino_cli.sh`
  - `tools\setup_arduino_cli.bat`
- current helper upload path:
  - `./tools/upload_cont_high_emg_reference.sh`
  - `tools\upload_cont_high_emg_reference.bat`

---

## 🔗 See Also

- [Sampling strategy](../../docs/sampling_strategy.md)
- [Serial protocol](../../docs/serial_protocol.md)
- [EMG lab guide](../../docs/labs/emg.md)
