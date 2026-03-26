# Session Presets

> Reusable JSON presets for the student GUI.

Use this folder when you want to load a ready-made classroom setup or save a configuration that students can reuse later.

---

## Start Here

Students can use the GUI buttons:

- `Load Preset`
- `Save Preset`

Current shipped examples:

- `ecg.json`
- `emg.json`
- `pulse_ox.json`
- `blood_pressure.json`

---

## What A Preset Stores

Each preset stores:

- the selected lab profile when one is used
- the active signals, names, preset types, and analog-port assignments
- the generated acquisition rate and timestamp field
- the default save folder and filename prefix
- the live-plot subplot layout

---

## How To Use Them In Class

Recommended classroom workflow:

1. launch the GUI
2. click `Load Preset`
3. choose the matching lab preset
4. confirm the board, port, and save folder
5. compile or upload if needed
6. start acquisition

Instructors or TAs can also save custom presets for a specific section or station.

---

## See Also

- [Python README](../README.md)
- [Student setup](../../docs/student_setup.md)
- [Lab guides](../../docs/labs/README.md)
