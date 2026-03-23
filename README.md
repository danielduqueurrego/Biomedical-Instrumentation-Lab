Biomedical Instrumentation Lab is organized by acquisition pattern first so students and instructors can reuse one software workflow across multiple lab types.

## Start Here

If you are a student or TA and just want to run a lab, use this short path:

1. Install Conda, then create the Python environment:
   - `cd python`
   - `conda env create -f environment.yml`
   - `conda activate biomed-lab`
   - `cd ..`
2. Set up Arduino CLI once:
   - macOS/Linux: `./tools/setup_arduino_cli.sh`
   - Windows: `tools\setup_arduino_cli.bat`
3. Run the system check:
   - `cd python`
   - `python system_check.py`
   - `cd ..`
4. Launch the student GUI:
   - Linux: `./launch_student_gui_linux.sh`
   - macOS: `./launch_student_gui_macos.command`
   - Windows: `launch_student_gui_windows.bat`
5. In the GUI:
   - select the detected board and port
   - load a lab preset such as `EMG`, `ECG`, `Pulse Oximetry`, or `Blood Pressure`
   - choose a save folder
   - compile/upload firmware if needed
   - click `Start Acquisition`
6. Your session is saved as one CSV file in the folder you choose.
   - the shipped presets default to `data/gui_sessions/`
   - each session CSV uses `row_type` such as `META`, `DATA`, `PHASE`, or `CYCLE`

Full setup details:
- `docs/student_setup.md`
- `docs/arduino_cli_setup.md`
- `examples/session_csv/README.md`

Primary architecture documents:
- `docs/acquisition_architecture.md`
- `docs/arduino_cli_setup.md`
- `docs/generated_firmware_workflow.md`
- `docs/labs/README.md`
- `docs/student_setup.md`
- `docs/sampling_strategy.md`
- `docs/serial_protocol.md`
- `docs/validation/README.md`

Top-level structure:
- `firmware/cont_high`: high-rate continuous waveform sketches such as EMG
- `firmware/cont_med`: medium-rate continuous waveform sketches such as ECG, Blood Pressure, and classroom demos
- `firmware/phased_cycle`: multi-phase optical acquisition sketches such as pulse oximetry
- `python/acquisition`: shared Python protocol, preset, serial, logging, and plotting helpers
- `python/acquisition/student_gui`: modular student GUI package split into connection, firmware, signal, plotting, session, and status modules
- `python/apps`: student-facing Python apps built on the shared acquisition helpers
- `python/session_presets`: reusable JSON presets for common lab sessions
- `examples/session_csv`: small synthetic session files showing how `row_type` logs look in practice
- `docs/labs`: classroom-facing lab guides for the major lab workflows
- `docs/validation`: hardware validation framework and reusable checklists

Current implemented baseline:
- `CONT_HIGH` Arduino UNO R4 WiFi EMG reference sketch using `t_us` timestamps at the manifest default of `2000` samples/s
- additional committed `CONT_HIGH` helper sketch for a simpler 1 kHz two-channel EMG reference upload path
- `CONT_MED` Arduino UNO R4 WiFi analog-bank demo using the shared `META` and `DATA` packet types
- generated student GUI firmware for continuous labs using selected signals, selected analog ports, and the highest selected preset rate
- committed `PHASED_CYCLE` PulseOx reference sketch for known-good bench validation and protocol checkout
- generated `PHASED_CYCLE` PulseOx firmware and logging path using shared `A0` to `A3` photodiode channels, `PHASE` and `CYCLE` packets, D6 for RED LED control, and D5 for IR LED control
- all current UNO R4 WiFi firmware paths set `analogReadResolution(14)` and report `META,adc_resolution_bits,14`
- refactored Tkinter student GUI with modular internals, session preset save/load, generated firmware compile/upload, collapsible panels, and multi-subplot live plotting
- one student-facing CSV per session, with `row_type` distinguishing `META`, `DATA`, `PHASE`, `CYCLE`, and error rows

Student setup stays minimal:
- one Conda environment
- `matplotlib` for plotting
- `pyserial` for serial communication
- Arduino CLI for command-line firmware compile and upload

Arduino CLI helper scripts:
- `tools/setup_arduino_cli.sh` or `tools/setup_arduino_cli.bat`
- `tools/upload_cont_med_three_channel.sh` or `tools/upload_cont_med_three_channel.bat`
- `tools/upload_cont_high_emg_reference.sh` or `tools/upload_cont_high_emg_reference.bat`

Each successful firmware compile also saves a timestamped Arduino code copy under `data/arduino_code_snapshots/`. GUI-driven compiles generate that code from the selected signals, highest selected preset rate, and PulseOx phase logic when the `PulseOx` preset is used. In PulseOx mode, red versus IR is inferred from the LED phase while the same four optical channels on `A0` to `A3` are sampled every phase.

Python student entry points:
- `python/system_check.py`
- `python/run_student_acquisition_gui.py`

Top-level student GUI launchers:
- Linux: `./launch_student_gui_linux.sh`
- macOS: `./launch_student_gui_macos.command`
- Windows: `launch_student_gui_windows.bat`

CI smoke tests:
- `.github/workflows/python-tests.yml` keeps the existing Python test run and adds Arduino CLI compile checks
- CI installs the `arduino:renesas_uno` core and compiles the committed reference sketches plus one generated example for each acquisition class
- CI is compile-only and does not attempt hardware upload or bench validation
