# Project Brief

> Short overview of the repository’s purpose, current scope, and teaching goals.

Use this document when you want the short project summary without reading the full root README.

---

## Start Here

Biomedical Instrumentation Lab supports classroom biomedical instrumentation activities built around:

- an Arduino UNO R4 WiFi
- a shared serial protocol
- a student-friendly Python GUI
- one-session CSV logging

The project is intended to stay simple enough for undergraduate lab use while still being transparent enough for instructors and contributors to inspect.

---

## Current Scope

The repo currently focuses on:

- Arduino UNO R4 WiFi firmware
- Python live plotting
- Python CSV logging
- reusable parsers and protocol helpers
- pattern-first repository architecture
- classroom presets for EMG, ECG, PulseOx, and Blood Pressure

---

## Acquisition Types

### Continuous waveform labs

Examples:

- EMG
- ECG
- Blood Pressure

Expected behavior:

- timestamped analog samples
- shared `META` and `DATA` packets
- one session CSV per run

### Sequenced optical lab

Current example:

- PulseOx

Expected behavior:

- raw phase logging
- corrected cycle logging
- live plotting of corrected values
- one session CSV per run with `PHASE` and `CYCLE` rows

Current phase order:

- `RED_ON`
- `DARK1`
- `IR_ON`
- `DARK2`

---

## Current PulseOx Board Model

The repo’s current PulseOx hardware model is:

- `A0 = reflective photodiode raw output`
- `A1 = transmission photodiode raw output`
- `A2 = filtered reflective photodiode output`
- `A3 = filtered transmission photodiode output`

Important rule:

- red versus IR is inferred from acquisition phase
- there are not separate red-only and IR-only analog pins

---

## Current Student Workflow

The intended classroom path is:

1. create or activate the Conda environment
2. set up Arduino CLI once
3. run the system check
4. launch the GUI
5. select a lab preset
6. compile or upload firmware if needed
7. start acquisition and save one CSV

---

## See Also

- [README.md](../README.md)
- [student_setup.md](./student_setup.md)
- [acquisition_architecture.md](./acquisition_architecture.md)
- [sampling_strategy.md](./sampling_strategy.md)
- [serial_protocol.md](./serial_protocol.md)
