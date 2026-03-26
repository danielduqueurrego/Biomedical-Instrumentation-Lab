# EMG Lab

> High-rate continuous EMG workflow for comparing raw and conditioned signal paths.

Use this guide when you are setting up the EMG lab in class or checking whether the current EMG configuration matches the repo defaults.

---

## Start Here

Recommended classroom path:

1. connect the Arduino UNO R4 WiFi
2. launch the student GUI
3. choose `EMG` from the lab dropdown or load `python/session_presets/emg.json`
4. confirm the four EMG rows are loaded on `A0` to `A3`
5. choose a save folder
6. compile and upload from the GUI or use the committed EMG reference sketch
7. start acquisition

---

## Quick Reference

| Item | Current default |
| --- | --- |
| Purpose | Compare raw EMG with conditioned EMG paths |
| Acquisition class | `CONT_HIGH` |
| Default sampling rate | `2000 samples/s` |
| Arduino timestamp field | `t_us` |
| Main packet types | `META`, `DATA`, optional `STAT`, optional `ERR` |
| Student preset | `python/session_presets/emg.json` |
| Reference sketch | `firmware/cont_high/uno_r4_wifi/emg_four_channel_demo/emg_four_channel_demo.ino` |

---

## Signal Set And Pin Mapping

Default Arduino UNO R4 WiFi mapping:

- `A0 = Raw EMG`
- `A1 = Rectified EMG`
- `A2 = Enveloped EMG`
- `A3 = Pressure`

These are the four default classroom signals:

- raw EMG
- rectified EMG
- enveloped EMG
- pressure

---

## Firmware And GUI Notes

Students can use either:

- the GUI-generated firmware path
- the committed EMG reference sketch

Current behavior to remember:

- EMG is a `CONT_HIGH` lab
- timing uses `t_us`
- the UNO R4 WiFi ADC is configured to `14-bit`
- the session CSV stores all `DATA` rows in one file

---

## Expected Output

The session CSV should contain:

- `META` rows that declare the sampling configuration
- `DATA` rows for the four EMG channels
- optional `STAT`, `ERR`, or `PARSE_ERROR` rows if something unusual happens

Students should usually start analysis by filtering to:

- `row_type=DATA`

---

## Troubleshooting

### The plot looks too slow or uneven

- confirm the EMG profile is using `CONT_HIGH`
- confirm the session metadata reports `t_us`
- confirm the configured rate is `2000 samples/s`

### The wrong channels are being plotted

- check the analog-port assignments on the left panel
- reload the EMG preset if needed

### Upload or acquisition fails

- confirm the board and port are detected
- rerun the system check if needed

---

## Screenshot Placeholder

Recommended screenshot location:

- `docs/screenshots/emg_live_plot_placeholder.svg`

Replace it later with a real classroom capture when available.

---

## See Also

- [Lab index](./README.md)
- [Student setup](../student_setup.md)
- [Sampling strategy](../sampling_strategy.md)
- [Validation tables](../validation/lab_validation_tables.md)
