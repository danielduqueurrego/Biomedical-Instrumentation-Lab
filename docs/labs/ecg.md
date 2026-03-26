# ECG Lab

> Medium-rate continuous ECG workflow for comparing raw, amplified, and comparator outputs.

Use this guide when you are preparing the ECG lab station or helping students confirm the expected ECG signals and rate.

---

## Start Here

Recommended classroom path:

1. connect the Arduino UNO R4 WiFi
2. launch the student GUI
3. choose `ECG` from the lab dropdown or load `python/session_presets/ecg.json`
4. confirm the three ECG rows are loaded on `A0` to `A2`
5. choose a save folder
6. compile and upload from the GUI
7. start acquisition

---

## Quick Reference

| Item | Current default |
| --- | --- |
| Purpose | Compare raw ECG with conditioned and comparator outputs |
| Acquisition class | `CONT_MED` |
| Default sampling rate | `500 samples/s` |
| Arduino timestamp field | `t_ms` |
| Main packet types | `META`, `DATA`, optional `STAT`, optional `ERR` |
| Student preset | `python/session_presets/ecg.json` |
| Firmware source | GUI-generated firmware |

---

## Signal Set And Pin Mapping

Default Arduino UNO R4 WiFi mapping:

- `A0 = Raw ECG`
- `A1 = Amplified ECG`
- `A2 = Comparator Output`

Default classroom signals:

- raw ECG
- amplified ECG
- comparator output

---

## Firmware And GUI Notes

Current behavior to remember:

- ECG is a `CONT_MED` lab
- timing uses `t_ms`
- the GUI generates firmware from the selected signals
- the session CSV stores all continuous data in one file

---

## Expected Output

The session CSV should contain:

- `META` rows describing the selected ports and rate
- `DATA` rows for the three ECG channels
- optional `STAT`, `ERR`, or `PARSE_ERROR` rows if relevant

Students should usually start by filtering to:

- `row_type=DATA`

---

## Troubleshooting

### The comparator channel looks flat

- verify that the comparator output is actually wired to `A2`
- confirm the selected ECG preset did not get overwritten

### The session rate looks wrong

- confirm the metadata reports `CONT_MED`
- confirm the reported rate is `500 samples/s`

### The board is not detected

- refresh the GUI board and port list
- run `python tools/arduino_cli.py board-list`

---

## Screenshot Placeholder

Suggested location for a future ECG screenshot:

- `docs/screenshots/ecg_live_plot.png`

---

## See Also

- [Lab index](./README.md)
- [Student setup](../student_setup.md)
- [Sampling strategy](../sampling_strategy.md)
- [Example session CSVs](../../examples/session_csv/README.md)
