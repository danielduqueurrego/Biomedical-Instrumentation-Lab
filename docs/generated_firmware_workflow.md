# Generated Firmware Workflow

> How the student GUI turns the current lab configuration into a temporary Arduino sketch for compile and upload.

Use this document when you need to understand what the GUI-generated firmware is doing. If you only want to run the lab, go back to [student_setup.md](./student_setup.md).

---

## Start Here

The student GUI does not always compile a fixed reference sketch directly. In most classroom cases, it generates a temporary Arduino UNO R4 WiFi sketch from the active lab configuration.

This keeps the workflow simple:

1. load a lab profile or session preset
2. review the selected signals and save folder
3. click compile or upload
4. inspect the saved Arduino code copy later if needed

Every successful compile saves a timestamped copy of the exact generated code under:

- `data/arduino_code_snapshots/arduino_code_YYYY_MM_DD_HH_MM_SS.ino`

---

## Continuous Workflow

If the selected signals are not PulseOx, the generated sketch uses the continuous workflow.

Current rules:

- use the highest default rate among the selected signal presets
- set the UNO R4 WiFi ADC to `14-bit` with `analogReadResolution(14)`
- emit only the selected analog ports
- send `META` plus `DATA` packets
- resolve to `CONT_HIGH` or `CONT_MED` from the selected rate

Timing behavior:

- `CONT_HIGH` emits `META,fields,t_us,...` and `DATA,t_us,...`
- `CONT_MED` emits `META,fields,t_ms,...` and `DATA,t_ms,...`

Example:

- selected presets: `EMG` at `2000 samples/s` and `Blood Pressure` at `200 samples/s`
- generated result: `CONT_HIGH` at `2000 samples/s`
- timing field: `t_us`

---

## PulseOx Workflow

If the selected signals use the `PulseOx` preset, the generated sketch switches to `PHASED_CYCLE`.

Current rules:

- all active signals must be `PulseOx` signals
- PulseOx uses the fixed UNO R4 WiFi mapping:
  - `A0 = reflective_raw`
  - `A1 = transmission_raw`
  - `A2 = reflective_filtered`
  - `A3 = transmission_filtered`
- generated firmware drives:
  - `D6 = RED LED`
  - `D5 = IR LED`

Phase sequence:

- `RED_ON`
- `DARK1`
- `IR_ON`
- `DARK2`

During every phase, the sketch:

- sets the ADC to `14-bit`
- samples all four analog PulseOx channels
- discards the first read after switching inputs
- averages two settled reads per channel
- emits one `PHASE` packet with all four channel values

After `DARK2`, the sketch emits one corrected `CYCLE` packet.

Corrected outputs:

- `reflective_raw_red_corr`
- `reflective_raw_ir_corr`
- `transmission_raw_red_corr`
- `transmission_raw_ir_corr`
- `reflective_filtered_red_corr`
- `reflective_filtered_ir_corr`
- `transmission_filtered_red_corr`
- `transmission_filtered_ir_corr`

Important model rule:

- red versus IR is inferred from the active phase
- red and IR are not separate analog inputs

---

## Blood Pressure Note

Blood Pressure stays on the continuous workflow.

Current behavior:

- no procedure-stage packets
- no `EVENT` rows
- students manually inflate and deflate the cuff while continuous `DATA` rows are logged

---

## What Gets Saved During A Run

### Generated sketch files

Temporary generated sketch folders are stored under:

- `data/generated_arduino_sketches/`

These are runtime artifacts and are not intended to be committed.

### Session logs

The student GUI saves one CSV per session.

That CSV can contain:

- `META` rows
- `DATA` rows for continuous labs
- `PHASE` and `CYCLE` rows for PulseOx
- `STAT`, `ERR`, or `PARSE_ERROR` rows when relevant

The `row_type` column is the first thing students should use to filter the file.

---

## Why Generated Firmware Is Still Student-Friendly

Even though the code is generated at runtime, the workflow stays simple for class use:

- students do not need to edit `.ino` files
- the GUI uses the selected lab configuration directly
- instructors can inspect the saved code copy after compile
- committed reference sketches still exist for known-good smoke tests and simpler demonstrations

---

## Migration Notes

- high-rate continuous generated firmware now uses `t_us`
- medium-rate continuous generated firmware still uses `t_ms`
- PulseOx uses the fixed four-channel shared photodiode model on `A0` to `A3`

---

## See Also

- [README.md](../README.md)
- [student_setup.md](./student_setup.md)
- [arduino_cli_setup.md](./arduino_cli_setup.md)
- [serial_protocol.md](./serial_protocol.md)
- [docs/labs/pulse_ox.md](./labs/pulse_ox.md)
