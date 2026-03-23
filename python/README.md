# Python acquisition tools

This folder contains the shared Python acquisition code plus student-facing launchers.

## Layout
- `acquisition/`: shared protocol, preset, serial, logging, and plotting helpers
- `acquisition/student_gui/`: modular Tkinter GUI package split by connection, firmware, signals, plotting, session controls, and status output
- `apps/`: student-facing apps built from the shared acquisition helpers
- `session_presets/`: reusable JSON session presets for common labs
- `run_*.py`: simple entry points for each app
- `launch_*.sh` and `launch_*.bat`: fallback launchers inside `python/`
- top-level `launch_student_gui_*`: primary beginner launchers for each OS

## Minimal setup
1. Install a free Conda-based Python distribution such as Miniconda or Anaconda.
2. Open a terminal in this `python` folder.
3. Create the environment:
   `conda env create -f environment.yml`
4. Activate it:
   `conda activate biomed-lab`
5. Run the system check:
   `python system_check.py`

## Development checks (optional for contributors)
Student setup stays minimal with `environment.yml`.

If you are contributing and want local tests, from `python/` create the dev environment:
- `conda env create -f environment-dev.yml`
- `conda activate biomed-lab-dev`

Run tests with either path style:
- from repository root: `pytest -q python/tests`
- from `python/`: `pytest -q tests`

Pull requests are expected to keep this fast test suite passing before merge.

## Main student GUI
The first student-facing GUI is a shared Arduino UNO R4 WiFi acquisition app built around the six standard analog inputs `A0` to `A5`.

Before running the Python app, upload the matching firmware from the repository root with:
- macOS/Linux: `./tools/upload_cont_med_three_channel.sh`
- Windows: `tools\\upload_cont_med_three_channel.bat`

Primary beginner launch (run from repository root):
- Linux: `./launch_student_gui_linux.sh`
- macOS: `./launch_student_gui_macos.command`
- Windows: `launch_student_gui_windows.bat`

Fallback launchers from this `python` folder (older path kept for compatibility):
- `python run_student_acquisition_gui.py`
- `./launch_student_acquisition_gui.sh`
- `launch_student_acquisition_gui.bat`

The new top-level launchers check PATH first and then common Conda install locations.

If a launcher reports Conda or `biomed-lab` errors, fix setup with:
1. `cd python`
2. `conda env create -f environment.yml`
3. return to repository root and re-run your OS launcher

The GUI lets students:
- use a top toolbar to load ready-made lab profiles for ECG, Pulse Oximetry, Blood Pressure, and EMG
- save the current session settings to a JSON preset and load them later
- select a board and let the GUI auto-fill the port from Arduino CLI
- review or override the detected serial port when needed
- choose a save folder and filename
- choose 1 to 6 signals
- assign each signal a name, preset, and analog port from `A0` to `A5`
- review preset sampling defaults
- start and stop acquisition
- choose how many live subplots to show
- choose which plotted series appear in each subplot
- view live plots
- log data automatically

Shipped session presets:
- `session_presets/ecg.json`
- `session_presets/emg.json`
- `session_presets/pulse_ox.json`
- `session_presets/blood_pressure.json`

Each preset stores:
- the selected lab profile or a custom configuration
- the active signals, names, presets, and analog-port assignments
- the generated acquisition class, default rate, and Arduino timestamp field
- the save folder and output filename prefix
- the subplot count and plotted-series selections

When one Arduino UNO R4 WiFi is connected, the GUI is expected to fill the board and port automatically.

Current toolbar behavior:
- each lab profile loads the requested signal names and analog-port defaults
- the GUI compile/upload path generates a shared UNO R4 analog capture sketch from the currently selected signals
- the generated sketch uses only the selected analog ports and the highest selected preset rate
- when the generated continuous acquisition resolves to `CONT_HIGH`, it emits `t_us` timestamps
- when the generated continuous acquisition resolves to `CONT_MED`, it emits `t_ms` timestamps
- Blood Pressure stays on the continuous `DATA` workflow
- when the selected signals use the `PulseOx` preset, all active signals must be `PulseOx` signals
- in PulseOx mode, the GUI uses the fixed board mapping `A0=reflective_raw`, `A1=transmission_raw`, `A2=reflective_filtered`, `A3=transmission_filtered`
- in PulseOx mode, the GUI locks each row to its fixed PulseOx analog input
- in PulseOx mode, the generated sketch drives D6 for RED and D5 for IR through `RED_ON`, `DARK1`, `IR_ON`, `DARK2`
- in PulseOx mode, the generated sketch emits raw `PHASE` packets with all four optical channels on every phase
- in PulseOx mode, the generated sketch emits corrected `CYCLE` packets with explicit RED-corrected and IR-corrected values for each path
- each successful firmware compile saves a timestamped Arduino code copy named `arduino_code_YYYY_MM_DD_HH_MM_SS.ino` under `../data/arduino_code_snapshots/`

Current live-plot behavior:
- subplot count can be set from 1 up to the number of plotted series
- changing the subplot count resets to a simple default split
- any plotted series can be assigned to one or more subplots with the `S1` onward selectors
- the signal reference line above the plot explains which plotted series each `S#` label represents
- the top toolbar can hide or restore the left setup panel and the bottom status log
- subplot legends are shown on the left side of each graph so the newest signal updates remain easier to see on the right
- PulseOx sessions plot corrected `CYCLE` values while raw `PHASE` values are still saved to CSV

See also:
- `../docs/generated_firmware_workflow.md`

## Existing reference CLI app
The original reference CLI app is still available from this folder with:
- `python run_cont_med_three_channel.py`
- `python run_cont_med_three_channel.py --port COM3`
- `./launch_cont_med_three_channel.sh`
- `launch_cont_med_three_channel.bat --port COM3`

If only one serial port is present, the app can auto-select it. If several ports are present, use `--port`.

## Output files
The student GUI saves files under the folder you choose, using your selected output filename.

The CLI reference app still saves one session folder under:
- `../data/cont_med/three_channel_data_demo/<timestamp>/`

See `../docs/student_setup.md` for the Windows, macOS, and Linux setup path.

Migration note:
- high-rate continuous sessions now log Arduino timestamps at microsecond resolution
- the `CONT_MED` three-channel reference app is unchanged and still uses `t_ms`
