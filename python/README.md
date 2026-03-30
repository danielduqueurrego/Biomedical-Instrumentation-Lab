# Python Acquisition Tools

> Shared Python code, launchers, presets, and the student-facing GUI.

Use this folder when you are setting up the Python side of the project or contributing to the student GUI and shared acquisition utilities.

---

## Start Here

If you are a student or TA, the main path is:

1. create the Conda environment from `environment.yml`
2. from the repository root, run a student doctor launcher
3. go back to the repository root
4. launch the student GUI with the top-level OS launcher

From this `python/` folder:

```bash
conda env create -f environment.yml
conda activate biomed-lab
```

Then from repository root run one of:

- Linux: `./launch_student_doctor_linux.sh`
- macOS: `./launch_student_doctor_macos.command`
- Windows: `launch_student_doctor_windows.bat`

---

## Folder Layout

- `acquisition/`: shared protocol, preset, serial, logging, and plotting helpers
- `acquisition/student_gui/`: modular Tkinter GUI package split by connection, firmware, signals, plotting, session controls, and status output
- `apps/`: student-facing apps built from the shared acquisition helpers
- `session_presets/`: reusable JSON session presets for common labs
- `run_*.py`: simple entry points for each app
- `launch_*.sh` and `launch_*.bat`: fallback launchers inside `python/`
- top-level `launch_student_gui_*`: primary beginner launchers for each OS

---

## Main Student GUI

The current student GUI is a shared Arduino UNO R4 WiFi acquisition app built around the six standard analog inputs `A0` to `A5`.

Primary beginner launch from the repository root:

- Linux: `./launch_student_gui_linux.sh`
- macOS: `./launch_student_gui_macos.command`
- Windows: `launch_student_gui_windows.bat`

Fallback launchers from this `python/` folder:

- `python run_student_acquisition_gui.py`
- `./launch_student_acquisition_gui.sh`
- `launch_student_acquisition_gui.bat`

---

## What The GUI Supports

Students can currently:

- load ready-made lab profiles for ECG, Pulse Oximetry, Blood Pressure, and EMG
- load or save reusable JSON session presets
- select a board and let Arduino CLI auto-fill the port
- review or override the detected serial port if needed
- choose a save folder and filename
- choose `1` to `6` active signals
- assign each signal a name, preset, and analog port from `A0` to `A5`
- review preset sampling defaults
- compile or upload firmware from the GUI
- start and stop acquisition
- choose how many live subplots to show
- choose which plotted series appear in each subplot
- hide the left setup panel or bottom status log to make more room for plots
- save one session CSV per run

---

## Important Current Behavior

### Continuous labs

- the generated sketch uses only the selected analog ports
- the generated sketch uses the highest selected preset rate
- `CONT_HIGH` emits `t_us`
- `CONT_MED` emits `t_ms`
- the UNO R4 WiFi ADC is configured to `14-bit`

### PulseOx

- all active signals must be `PulseOx`
- PulseOx uses the fixed map:
  - `A0 = reflective_raw`
  - `A1 = transmission_raw`
  - `A2 = reflective_filtered`
  - `A3 = transmission_filtered`
- generated firmware drives `D6` for RED and `D5` for IR
- generated firmware emits `PHASE` and corrected `CYCLE` rows
- the live plot shows corrected `CYCLE` values

### Firmware uploads

- compile and upload actions use timeouts
- missing-board uploads fail fast with a readable message
- each successful compile saves `arduino_code_YYYY_MM_DD_HH_MM_SS.ino` under `../data/arduino_code_snapshots/`

---

## Session Presets

Shipped presets:

- `session_presets/ecg.json`
- `session_presets/emg.json`
- `session_presets/pulse_ox.json`
- `session_presets/blood_pressure.json`

Each preset stores:

- selected lab profile or custom configuration
- active signals, names, presets, and analog-port assignments
- generated acquisition class, default rate, and timestamp field
- save folder and filename prefix
- subplot count and plotted-series selections

---

## Output Files

The student GUI saves one CSV per session in the folder the user chooses.

That CSV can contain:

- `META`
- `DATA`
- `PHASE`
- `CYCLE`
- `STAT`
- `ERR`
- `PARSE_ERROR`

Use the `row_type` column to filter what you need.

The older CLI reference app still saves one timestamped session folder under:

- `../data/cont_med/three_channel_data_demo/<timestamp>/`

Inside that folder it writes one `session.csv`.

---

## Contributor Checks

Student setup stays minimal with `environment.yml`. Contributors can also use `environment-dev.yml`.

Typical checks:

- from repository root: `pytest -q python/tests`
- from `python/`: `pytest -q tests`
- `python -m compileall python`

---

## See Also

- [README.md](../README.md)
- [Student setup](../docs/student_setup.md)
- [Generated firmware workflow](../docs/generated_firmware_workflow.md)
- [Session presets README](./session_presets/README.md)
