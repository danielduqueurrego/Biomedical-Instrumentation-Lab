# Student Setup

> Beginner-friendly setup guide for Windows, macOS, and Linux.

Use this guide when you are preparing a classroom computer or helping a student get to their first live plot. If you only want the short version, see the quick start in [README.md](../README.md).

---

## Start Here

Students only need:

- one Conda-based Python distribution such as Miniconda or Anaconda
- Arduino CLI
- a USB data cable for the Arduino board

The intended path is:

1. create one Conda environment
2. run the student doctor check
3. prepare Arduino CLI once
4. launch the GUI
5. load a lab preset
6. start acquisition
7. save one CSV per session

---

## Quick Path By Operating System

### Windows

1. Install Miniconda or Anaconda.
2. Install Arduino CLI.
3. Open Command Prompt or PowerShell in the repository root.
4. Create and activate the environment:
   ```bat
   cd python
   conda env create -f environment.yml
   conda activate biomed-lab
   cd ..
   ```
5. Prepare Arduino CLI once:
   ```bat
   tools\setup_arduino_cli.bat
   ```
6. Run the doctor check:
   ```bat
   launch_student_doctor_windows.bat
   ```
7. Launch the GUI:
   ```bat
   launch_student_gui_windows.bat
   ```

### macOS

1. Install Miniconda or Anaconda.
2. Install Arduino CLI.
3. Open Terminal in the repository root.
4. Create and activate the environment:
   ```bash
   cd python
   conda env create -f environment.yml
   conda activate biomed-lab
   cd ..
   ```
5. Prepare Arduino CLI once:
   ```bash
   ./tools/setup_arduino_cli.sh
   ```
6. Run the doctor check:
   ```bash
   ./launch_student_doctor_macos.command
   ```
7. Launch the GUI:
   ```bash
   ./launch_student_gui_macos.command
   ```

### Linux

1. Install Miniconda or Anaconda.
2. Install Arduino CLI.
3. Make sure your user has serial-port access if required by the OS.
4. Open Terminal in the repository root.
5. Create and activate the environment:
   ```bash
   cd python
   conda env create -f environment.yml
   conda activate biomed-lab
   cd ..
   ```
6. Prepare Arduino CLI once:
   ```bash
   ./tools/setup_arduino_cli.sh
   ```
7. Run the doctor check:
   ```bash
   ./launch_student_doctor_linux.sh
   ```
8. Launch the GUI:
   ```bash
   ./launch_student_gui_linux.sh
   ```

---

## What To Do In The GUI

Once the GUI opens:

1. confirm the board and port are detected
2. choose a lab from the lab dropdown
3. optionally load a JSON session preset
4. choose the save folder
5. compile or upload firmware if needed
6. click `Start Acquisition`

In the most common classroom case, one connected Arduino UNO R4 WiFi should auto-fill the board and port after refresh.

---

## Current GUI Features

The current student GUI lets students:

- load lab profiles from a dropdown
- load or save reusable JSON session presets
- select the board target
- let Arduino CLI auto-detect the connected board port
- choose a save folder and output filename
- use an auto-updated timestamp suffix in the output filename
- choose between `1` and `6` active signals
- assign a name, preset, and analog port to each active signal
- choose how many live subplots to display
- choose which plotted series appear in each subplot
- compile or upload firmware from the GUI
- start and stop acquisition
- hide the left panel or bottom status log to make more room for plots
- save one CSV per session

---

## What The Student Doctor Verifies

From the repository root, run one of:

- Linux: `./launch_student_doctor_linux.sh`
- macOS: `./launch_student_doctor_macos.command`
- Windows: `launch_student_doctor_windows.bat`

The doctor command runs the system checks and then tries to list connected boards using Arduino CLI.

## What The System Check Verifies

Run from the `python/` folder:

```bash
python system_check.py
```

The system check verifies:

- `tkinter`
- `matplotlib`
- `pyserial`
- `arduino-cli`
- visible serial ports

---

## Session Presets

The repo ships example presets in:

- `python/session_presets/ecg.json`
- `python/session_presets/emg.json`
- `python/session_presets/pulse_ox.json`
- `python/session_presets/blood_pressure.json`

Each preset stores:

- the selected lab profile
- active signal names, preset types, and analog ports
- the generated acquisition class and default rate
- the save folder and filename prefix
- subplot layout and plotted-series selections

---

## What The Generated Firmware Does

The GUI-generated firmware workflow currently:

- generates Arduino code from the current signal selection
- uses the highest selected preset rate
- emits only the selected analog ports
- uses `t_us` when the continuous session resolves to `CONT_HIGH`
- uses `t_ms` when the continuous session resolves to `CONT_MED`
- saves a timestamped copy of the compiled Arduino code for review
- keeps Blood Pressure on the continuous `DATA` workflow

PulseOx-specific behavior:

- all active signals must be `PulseOx`
- the fixed hardware map is:
  - `A0 = reflective_raw`
  - `A1 = transmission_raw`
  - `A2 = reflective_filtered`
  - `A3 = transmission_filtered`
- the GUI locks those PulseOx rows to the correct analog inputs
- generated firmware drives `D6` for RED and `D5` for IR
- generated firmware emits raw `PHASE` rows and corrected `CYCLE` rows in the same session CSV

For more detail, see [generated_firmware_workflow.md](./generated_firmware_workflow.md).

---

## Where Files Are Saved

### Session data

The GUI saves one CSV per session in the folder the student chooses.

That CSV can contain:

- `META`
- `DATA`
- `PHASE`
- `CYCLE`
- `STAT`
- `ERR`
- `PARSE_ERROR`

Use the `row_type` column to filter the rows you care about.

### Arduino code copies

Every successful compile saves a copy of the generated sketch under:

- `data/arduino_code_snapshots/arduino_code_YYYY_MM_DD_HH_MM_SS.ino`

---

## Troubleshooting

### The GUI does not find the board

- reconnect the board
- run `python tools/arduino_cli.py board-list`
- refresh the GUI board and port list

### Firmware upload fails immediately

This usually means:

- no supported board was detected
- the wrong port is selected
- another program is holding the serial port

### Linux upload shows a permissions error

- check that your user has access to the serial device
- reconnect the board after fixing permissions

---

## Official References

- Anaconda and Miniconda downloads: https://www.anaconda.com/download
- Conda environment files: https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html
- Arduino CLI installation: https://docs.arduino.cc/arduino-cli/installation
- Arduino CLI getting started: https://docs.arduino.cc/arduino-cli/getting-started/
- Linux port access help: https://support.arduino.cc/hc/en-us/articles/360016495679-Fix-port-access-on-Linux

---

## See Also

- [README.md](../README.md)
- [arduino_cli_setup.md](./arduino_cli_setup.md)
- [generated_firmware_workflow.md](./generated_firmware_workflow.md)
- [docs/labs/README.md](./labs/README.md)
- [examples/session_csv/README.md](../examples/session_csv/README.md)
