# Student setup

This guide is the beginner-friendly setup path for Windows, macOS, and Linux.

## Software students need

Students only need:
- one Conda-based Python installation such as Miniconda or Anaconda
- Arduino CLI
- a USB data cable for the Arduino board

After that, the intended workflow is:
1. create one Conda environment,
2. run one system check,
3. compile or upload firmware from the GUI or Arduino CLI,
4. launch the Python GUI from a top-level starter script,
5. save data automatically.

## Windows

### Install software
1. Install Miniconda or Anaconda from the official Anaconda site.
2. Install Arduino CLI from the official Arduino CLI documentation.
3. Make sure `arduino-cli.exe` is on `PATH`, or set the `ARDUINO_CLI` environment variable to its full path.

### Project setup
1. Open Command Prompt or PowerShell.
2. Go to the repository root, then enter `python`:
   `cd python`
3. Create the Conda environment:
   `conda env create -f environment.yml`
4. Activate it:
   `conda activate biomed-lab`
5. Run the system check:
   `python system_check.py`
6. Return to the repository root before first run:
   `cd ..`

### First run (primary beginner path)
1. Go to the repository root.
2. Prepare Arduino CLI once:
   `tools\setup_arduino_cli.bat`
3. Upload the reference firmware:
   `tools\upload_cont_med_three_channel.bat`
4. Launch the GUI from the repository root:
   `launch_student_gui_windows.bat`

### Fallback / advanced launch path
If needed, the older launcher still works from the `python` folder:
1. From the repository root, enter `python`:
   `cd python`
2. Launch the GUI:
   `launch_student_acquisition_gui.bat`
3. Return to the repository root when finished:
   `cd ..`

## macOS

### Install software
1. Install Miniconda or Anaconda from the official Anaconda site.
2. Install Arduino CLI from the official Arduino CLI documentation.
3. Make sure `arduino-cli` is on `PATH`.

### Project setup
1. Open Terminal.
2. Go to the repository root, then enter `python`:
   `cd python`
3. Create the Conda environment:
   `conda env create -f environment.yml`
4. Activate it:
   `conda activate biomed-lab`
5. Run the system check:
   `python system_check.py`
6. Return to the repository root before first run:
   `cd ..`

### First run (primary beginner path)
1. Go to the repository root.
2. Prepare Arduino CLI once:
   `./tools/setup_arduino_cli.sh`
3. Upload a reference firmware (choose one):
   `./tools/upload_cont_med_three_channel.sh`
   `./tools/upload_cont_high_emg_reference.sh`
4. Launch the GUI from the repository root:
   `./launch_student_gui_macos.command`

### Fallback / advanced launch path
If needed, the older launcher still works from the `python` folder:
1. From the repository root, enter `python`:
   `cd python`
2. Launch the GUI:
   `./launch_student_acquisition_gui.sh`
3. Return to the repository root when finished:
   `cd ..`

## Linux

### Install software
1. Install Miniconda or Anaconda from the official Anaconda site.
2. Install Arduino CLI from the official Arduino CLI documentation.
3. Make sure `arduino-cli` is on `PATH`.
4. If needed, follow Arduino's Linux serial-port permission instructions.

### Project setup
1. Open Terminal.
2. Go to the repository root, then enter `python`:
   `cd python`
3. Create the Conda environment:
   `conda env create -f environment.yml`
4. Activate it:
   `conda activate biomed-lab`
5. Run the system check:
   `python system_check.py`
6. Return to the repository root before first run:
   `cd ..`

### First run (primary beginner path)
1. Go to the repository root.
2. Prepare Arduino CLI once:
   `./tools/setup_arduino_cli.sh`
3. Upload a reference firmware (choose one):
   `./tools/upload_cont_med_three_channel.sh`
   `./tools/upload_cont_high_emg_reference.sh`
4. Launch the GUI from the repository root:
   `./launch_student_gui_linux.sh`

### Fallback / advanced launch path
If needed, the older launcher still works from the `python` folder:
1. From the repository root, enter `python`:
   `cd python`
2. Launch the GUI:
   `./launch_student_acquisition_gui.sh`
3. Return to the repository root when finished:
   `cd ..`

## What the system check verifies

The system check script verifies:
- `tkinter`
- `matplotlib`
- `pyserial`
- `arduino-cli`
- visible serial ports

Run it with:
- from the repository root:
  - `cd python`
  - `python system_check.py`
  - `cd ..`

## What the first GUI supports

The first GUI allows students to:
- load lab profiles from a lab dropdown
- load or save reusable session presets in JSON format
- select the current board target
- let Arduino CLI auto-detect the connected board port
- review the detected serial port if more than one board or port is present
- choose a save folder and output filename
- use an auto-updated timestamp suffix in the output filename
- choose between 1 and 6 active signals
- assign a name, preset, and analog port to each active signal
- choose how many live subplots to display
- choose which plotted series appear in each subplot
- review preset sampling defaults
- compile or upload firmware from the GUI
- start and stop acquisition
- see live plots
- log data to CSV

The repository includes example session presets in:
- `python/session_presets/ecg.json`
- `python/session_presets/emg.json`
- `python/session_presets/pulse_ox.json`
- `python/session_presets/blood_pressure.json`

Each session preset stores:
- the selected lab profile when one is used
- the active signal names, preset types, and analog ports
- the generated acquisition class and default sampling rate
- the save folder and filename prefix
- the subplot layout and plotted-series selections

The GUI-generated firmware workflow:
- generates Arduino code from the current signal selection
- uses the highest selected preset rate
- emits only the selected analog ports
- uses `t_us` timing when the generated continuous session resolves to `CONT_HIGH`
- uses `t_ms` timing when the generated continuous session resolves to `CONT_MED`
- saves a timestamped copy of the compiled Arduino code for review
- keeps Blood Pressure on the continuous `DATA` workflow
- if the selected signals use the `PulseOx` preset, all active signals must be `PulseOx`
- if the selected signals use the `PulseOx` preset, the GUI uses the fixed hardware mapping:
  - `A0 = reflective_raw`
  - `A1 = transmission_raw`
  - `A2 = reflective_filtered`
  - `A3 = transmission_filtered`
- when a row uses the `PulseOx` preset, the GUI locks that row to its fixed PulseOx analog input
- adds PulseOx LED sequencing on `D6` and `D5` when the `PulseOx` preset is used
- emits raw `PHASE` packets with all four optical channels during every phase
- emits corrected `CYCLE` packets with explicit RED-corrected and IR-corrected values for each optical path
- saves PulseOx raw phases to `<output>_phase.csv` and corrected cycles to `<output>_cycle.csv`

The live-plot workflow:
- uses `S1` onward as short plotted-series labels in the plot-layout controls
- shows a signal reference line above the plot so students can match `S1` to the full plotted series name
- lets one signal appear in more than one subplot when comparison views are helpful
- resets to a simple default subplot split whenever the subplot count changes
- lets students hide or restore the left setup panel and bottom status log from the top toolbar
- places subplot legends on the left side of each graph

For PulseOx sessions, the plotted series are the corrected `CYCLE` outputs rather than the raw analog channel names.

In the most common case, where one Arduino UNO R4 WiFi is connected, the GUI should fill the board and port automatically after refresh.

For more detail on generated Arduino code, see:
- `docs/generated_firmware_workflow.md`

Migration note:
- high-rate continuous labs such as EMG now use microsecond Arduino timestamps
- medium-rate labs such as ECG and Blood Pressure remain on millisecond Arduino timestamps

## Official references

- Anaconda and Miniconda downloads: https://www.anaconda.com/download
- Conda environment files: https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html
- Arduino CLI installation: https://docs.arduino.cc/arduino-cli/installation
- Arduino CLI getting started: https://docs.arduino.cc/arduino-cli/getting-started/
- Linux port access help: https://support.arduino.cc/hc/en-us/articles/360016495679-Fix-port-access-on-Linux
