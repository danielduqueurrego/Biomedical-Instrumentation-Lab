# Session presets

This folder contains example GUI session presets in JSON format.

Students can load them from the main GUI with:
- `Load Preset`

Students can also save their own reusable presets with:
- `Save Preset`

The shipped examples are:
- `ecg.json`
- `emg.json`
- `pulse_ox.json`
- `blood_pressure.json`

Each preset stores:
- the selected lab profile when one is used
- the active signals, names, presets, and analog-port assignments
- the generated acquisition rate and timestamp field
- the default save folder and filename prefix
- the live-plot subplot layout
