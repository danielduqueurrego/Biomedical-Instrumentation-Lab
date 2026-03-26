# Acquisition Architecture

> Repo-level guide to how the project is organized and how each lab fits into the shared acquisition model.

Use this document when you need the big-picture structure of the repository, not the step-by-step student setup. If you are trying to run hardware quickly, start with [README.md](../README.md) and [student_setup.md](./student_setup.md).

---

## Start Here

The repository is organized by **acquisition pattern first**, then by lab or reference sketch. This keeps the student workflow consistent even when the sensing method changes.

The three acquisition classes used across the repo are:

| Acquisition class | Use it for | Main packets | Timing rule |
| --- | --- | --- | --- |
| `CONT_HIGH` | High-rate waveforms such as EMG | `META`, `DATA`, `STAT`, `ERR` | Use `t_us` |
| `CONT_MED` | Medium-rate waveforms such as ECG and Blood Pressure | `META`, `DATA`, `STAT`, `ERR` | Use `t_ms` |
| `PHASED_CYCLE` | Multi-phase measurements such as PulseOx | `META`, `PHASE`, `CYCLE`, `STAT`, `ERR` | Use `t_us` |

---

## Why The Repo Is Structured This Way

Pattern-first organization makes it easier to:

- reuse firmware and Python logging rules across multiple labs
- keep the serial protocol consistent
- keep the student GUI simple even when lab behavior changes
- separate beginner-facing workflows from deeper development work

In practice, this means a student can still follow the same basic workflow:

1. connect the board
2. launch the GUI
3. load a lab profile or preset
4. compile or upload firmware if needed
5. start acquisition
6. save one session CSV

---

## Repository Layout

```text
firmware/
  cont_high/
    uno_r4_wifi/
      <lab_name>/
  cont_med/
    uno_r4_wifi/
      <lab_name>/
  phased_cycle/
    uno_r4_wifi/
      <lab_name>/

python/
  acquisition/
    architecture.py
    presets.py
    protocol.py
    student_gui/
  apps/
  session_presets/

docs/
  labs/
  validation/

examples/
  session_csv/
```

What each area is for:

- `firmware/`: committed reference sketches, organized by acquisition class
- `python/acquisition/`: shared protocol, preset, plotting, logging, and firmware-generation logic
- `python/acquisition/student_gui/`: modular Tkinter GUI implementation
- `python/session_presets/`: reusable classroom presets in JSON format
- `docs/labs/`: student-facing and TA-facing lab guides
- `docs/validation/`: bench-validation workflow and templates
- `examples/session_csv/`: example one-file session logs

---

## How The Classes Behave

### `CONT_HIGH`

Use `CONT_HIGH` for high-rate waveform capture where millisecond timing is not precise enough.

Current repo expectations:

- save every sample
- plot a rolling view instead of redrawing on every sample
- log `DATA,t_us,...`
- use the manifest default rate for the selected lab or preset

Current example:

- EMG

### `CONT_MED`

Use `CONT_MED` for continuous waveforms where millisecond timing is sufficient and the student benefit is clarity rather than maximum throughput.

Current repo expectations:

- save every sample
- log `DATA,t_ms,...`
- use live plotting that stays readable during class

Current examples:

- ECG
- Blood Pressure
- simple analog reference demos

### `PHASED_CYCLE`

Use `PHASED_CYCLE` when one meaningful cycle is reconstructed from several timed phase measurements.

Current repo expectations:

- save both `PHASE` and `CYCLE` rows in the same session CSV
- keep the phase order explicit in the protocol
- plot corrected cycle values by default

Current example:

- PulseOx

---

## Current Lab Mapping

| Lab | Acquisition class | Default rate | Student-facing workflow |
| --- | --- | --- | --- |
| EMG | `CONT_HIGH` | `2000 samples/s` | GUI preset or committed EMG reference sketch |
| ECG | `CONT_MED` | `500 samples/s` | GUI preset and generated firmware |
| PulseOx | `PHASED_CYCLE` | `100 cycles/s` | GUI preset or committed PulseOx reference sketch |
| Blood Pressure | `CONT_MED` | `200 samples/s` | GUI preset and generated firmware |

---

## Design Rules Kept Across The Repo

- keep Arduino and Python responsibilities clearly separated
- keep the serial protocol human-readable first
- keep student installation minimal
- keep logging reliable even when plotting is simplified
- let the manifest and shared protocol drive the rest of the implementation

---

## See Also

- [README.md](../README.md)
- [student_setup.md](./student_setup.md)
- [sampling_strategy.md](./sampling_strategy.md)
- [serial_protocol.md](./serial_protocol.md)
- [generated_firmware_workflow.md](./generated_firmware_workflow.md)
- [docs/labs/README.md](./labs/README.md)
