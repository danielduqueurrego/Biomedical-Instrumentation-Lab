# Blood Pressure Lab

> Continuous waveform workflow for pressure acquisition during manual cuff inflation and deflation.

Use this guide when you are preparing the blood-pressure station or confirming the current board mapping and logging behavior.

---

## Start Here

Recommended classroom path:

1. connect the Arduino UNO R4 WiFi
2. launch the student GUI
3. choose `Blood Pressure` from the lab dropdown or load `python/session_presets/blood_pressure.json`
4. confirm the four Blood Pressure rows are loaded on `A0` to `A3`
5. choose a save folder
6. compile and upload from the GUI
7. start acquisition while the student manually inflates and deflates the cuff

---

## Quick Reference

| Item | Current default |
| --- | --- |
| Purpose | Record pressure waveforms and supporting optical channels during manual cuff operation |
| Acquisition class | `CONT_MED` |
| Default sampling rate | `200 samples/s` |
| Arduino timestamp field | `t_ms` |
| Main packet types | `META`, `DATA`, optional `STAT`, optional `ERR` |
| Student preset | `python/session_presets/blood_pressure.json` |
| Firmware source | GUI-generated firmware |

---

## Signal Set And Pin Mapping

Default Arduino UNO R4 WiFi mapping:

- `A0 = Raw Pressure`
- `A1 = Filtered Pressure`
- `A2 = Red PD`
- `A3 = IR PD`

Default classroom signals:

- raw pressure
- filtered pressure
- red PD
- IR PD

Important classroom note:

- Blood Pressure is treated as a continuous waveform lab
- students manually control cuff inflation and deflation
- the project does not emit procedure-stage events for this lab

---

## Firmware And GUI Notes

Current behavior to remember:

- Blood Pressure uses `CONT_MED`
- timing uses `t_ms`
- the GUI generates firmware from the selected configuration
- the session CSV stores all continuous rows in one file

---

## Expected Output

The session CSV should contain:

- `META` rows describing the selected ports and rate
- `DATA` rows for the pressure and photodiode channels
- optional `STAT`, `ERR`, or `PARSE_ERROR` rows if relevant

Students should usually start analysis by filtering to:

- `row_type=DATA`

---

## Troubleshooting

### The pressure waveform does not change during cuff operation

- confirm the pressure channels are on `A0` and `A1`
- verify that the cuff hardware is connected to the expected board inputs

### The session looks too slow

- confirm the metadata reports `200 samples/s`
- confirm the session is running as `CONT_MED`

### Students are looking for event markers

- remind them that this lab does not use procedure-stage packets
- inflation and deflation are recorded as part of the continuous waveform only

---

## Screenshot Placeholder

Suggested location for a future Blood Pressure screenshot:

- `docs/screenshots/blood_pressure_live_plot.png`

---

## See Also

- [Lab index](./README.md)
- [Student setup](../student_setup.md)
- [Sampling strategy](../sampling_strategy.md)
- [Validation tables](../validation/lab_validation_tables.md)
