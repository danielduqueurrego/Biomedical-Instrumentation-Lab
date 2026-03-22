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
4. launch the Python GUI,
5. save data automatically.

## Windows

### Install software
1. Install Miniconda or Anaconda from the official Anaconda site.
2. Install Arduino CLI from the official Arduino CLI documentation.
3. Make sure `arduino-cli.exe` is on `PATH`, or set the `ARDUINO_CLI` environment variable to its full path.

### Project setup
1. Open Command Prompt or PowerShell.
2. Go to the repository `python` folder.
3. Create the Conda environment:
   `conda env create -f environment.yml`
4. Activate it:
   `conda activate biomed-lab`
5. Run the system check:
   `python system_check.py`

### First run
1. Go to the repository root.
2. Prepare Arduino CLI once:
   `tools\\setup_arduino_cli.bat`
3. Upload the reference firmware:
   `tools\\upload_cont_med_three_channel.bat`
4. Go back to the `python` folder.
5. Launch the GUI:
   `launch_student_acquisition_gui.bat`

## macOS

### Install software
1. Install Miniconda or Anaconda from the official Anaconda site.
2. Install Arduino CLI from the official Arduino CLI documentation.
3. Make sure `arduino-cli` is on `PATH`.

### Project setup
1. Open Terminal.
2. Go to the repository `python` folder.
3. Create the Conda environment:
   `conda env create -f environment.yml`
4. Activate it:
   `conda activate biomed-lab`
5. Run the system check:
   `python system_check.py`

### First run
1. Go to the repository root.
2. Prepare Arduino CLI once:
   `./tools/setup_arduino_cli.sh`
3. Upload the reference firmware:
   `./tools/upload_cont_med_three_channel.sh`
4. Go back to the `python` folder.
5. Launch the GUI:
   `./launch_student_acquisition_gui.sh`

## Linux

### Install software
1. Install Miniconda or Anaconda from the official Anaconda site.
2. Install Arduino CLI from the official Arduino CLI documentation.
3. Make sure `arduino-cli` is on `PATH`.
4. If needed, follow Arduino's Linux serial-port permission instructions.

### Project setup
1. Open Terminal.
2. Go to the repository `python` folder.
3. Create the Conda environment:
   `conda env create -f environment.yml`
4. Activate it:
   `conda activate biomed-lab`
5. Run the system check:
   `python system_check.py`

### First run
1. Go to the repository root.
2. Prepare Arduino CLI once:
   `./tools/setup_arduino_cli.sh`
3. Upload the reference firmware:
   `./tools/upload_cont_med_three_channel.sh`
4. Go back to the `python` folder.
5. Launch the GUI:
   `./launch_student_acquisition_gui.sh`

## What the system check verifies

The system check script verifies:
- `tkinter`
- `matplotlib`
- `pyserial`
- `arduino-cli`
- visible serial ports

Run it with:
- `python system_check.py`

## What the first GUI supports

The first GUI allows students to:
- load lab profiles from a lab dropdown
- select the current board target
- let Arduino CLI auto-detect the connected board port
- review the detected serial port if more than one board or port is present
- choose a save folder and output filename
- use an auto-updated timestamp suffix in the output filename
- choose between 1 and 6 active signals
- assign a name, preset, and analog port to each active signal
- choose how many live subplots to display
- choose which configured signals appear in each subplot
- review preset sampling defaults
- compile or upload firmware from the GUI
- start and stop acquisition
- see live plots
- log data to CSV

The GUI-generated firmware workflow:
- generates Arduino code from the current signal selection
- uses the highest selected preset rate
- emits only the selected analog ports
- saves a timestamped copy of the compiled Arduino code for review
- adds PulseOx LED sequencing on `D6` and `D5` when the `PulseOx` preset is used

The live-plot workflow:
- uses `S1` to `S6` as short signal labels in the plot-layout controls
- shows a signal reference line above the plot so students can match `S1` to the full configured name
- lets one signal appear in more than one subplot when comparison views are helpful
- resets to a simple default subplot split whenever the subplot count changes

In the most common case, where one Arduino UNO R4 WiFi is connected, the GUI should fill the board and port automatically after refresh.

For more detail on generated Arduino code, see:
- `docs/generated_firmware_workflow.md`

## Official references

- Anaconda and Miniconda downloads: https://www.anaconda.com/download
- Conda environment files: https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html
- Arduino CLI installation: https://docs.arduino.cc/arduino-cli/installation
- Arduino CLI getting started: https://docs.arduino.cc/arduino-cli/getting-started/
- Linux port access help: https://support.arduino.cc/hc/en-us/articles/360016495679-Fix-port-access-on-Linux
