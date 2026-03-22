# Python acquisition tools

This folder contains the shared Python acquisition code plus student-facing launchers.

## Layout
- `acquisition/`: shared protocol, preset, serial, logging, and plotting helpers
- `apps/`: student-facing apps built from the shared acquisition helpers
- `run_*.py`: simple entry points for each app
- `launch_*.sh` and `launch_*.bat`: beginner-friendly launcher scripts

## Minimal setup
1. Install a free Conda-based Python distribution such as Miniconda or Anaconda.
2. Open a terminal in this `python` folder.
3. Create the environment:
   `conda env create -f environment.yml`
4. Activate it:
   `conda activate biomed-lab`
5. Run the system check:
   `python system_check.py`

## Main student GUI
The first student-facing GUI is a shared Arduino UNO R4 WiFi acquisition app built around the six standard analog inputs `A0` to `A5`.

Before running the Python app, upload the matching firmware from the repository root with:
- macOS/Linux: `./tools/upload_cont_med_three_channel.sh`
- Windows: `tools\\upload_cont_med_three_channel.bat`

Run it from this folder with:
- `python run_student_acquisition_gui.py`
- `./launch_student_acquisition_gui.sh`
- `launch_student_acquisition_gui.bat`

The GUI lets students:
- use a top toolbar to load ready-made lab profiles for ECG, Pulse Oximetry, Blood Pressure, and EMG
- select a board and let the GUI auto-fill the port from Arduino CLI
- review or override the detected serial port when needed
- choose a save folder and filename
- choose 1 to 6 signals
- assign each signal a name, preset, and analog port from `A0` to `A5`
- review preset sampling defaults
- start and stop acquisition
- view live plots
- log data automatically

When one Arduino UNO R4 WiFi is connected, the GUI is expected to fill the board and port automatically.

Current toolbar behavior:
- each lab profile loads the requested signal names and analog-port defaults
- the GUI compile/upload path generates a shared UNO R4 analog capture sketch from the currently selected signals
- the generated sketch uses only the selected analog ports and the highest selected preset rate
- the Pulse Oximetry profile does not start the phased-cycle implementation yet
- each successful firmware compile saves a timestamped Arduino code copy named `arduino_code_YYYY_MM_DD_HH_MM_SS.ino` under `../data/arduino_code_snapshots/`

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
