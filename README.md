Biomedical Instrumentation Lab is organized by acquisition pattern first so students and instructors can reuse one software workflow across multiple lab types.

Primary architecture documents:
- `docs/acquisition_architecture.md`
- `docs/arduino_cli_setup.md`
- `docs/generated_firmware_workflow.md`
- `docs/student_setup.md`
- `docs/sampling_strategy.md`
- `docs/serial_protocol.md`

Top-level structure:
- `firmware/cont_high`: high-rate continuous waveform sketches such as EMG
- `firmware/cont_med`: medium-rate continuous waveform sketches such as ECG, Blood Pressure, and classroom demos
- `firmware/phased_cycle`: multi-phase optical acquisition sketches such as pulse oximetry
- `python/acquisition`: shared Python protocol, preset, serial, logging, and plotting helpers
- `python/apps`: student-facing Python apps built on the shared acquisition helpers

Current implemented baseline:
- `CONT_MED` Arduino UNO R4 WiFi analog-bank demo using the shared `META` and `DATA` packet types
- generated student GUI firmware for continuous labs using selected signals, selected analog ports, and the highest selected preset rate
- generated `PHASED_CYCLE` PulseOx firmware and logging path using `PHASE` and `CYCLE` packets, D6 for RED LED control, and D5 for IR LED control
- first Tkinter GUI foundation for student acquisition setup, lab-profile loading, generated firmware compile/upload, collapsible panels, and multi-subplot live plotting

Student setup stays minimal:
- one Conda environment
- `matplotlib` for plotting
- `pyserial` for serial communication
- Arduino CLI for command-line firmware compile and upload

Arduino CLI helper scripts:
- `tools/setup_arduino_cli.sh` or `tools/setup_arduino_cli.bat`
- `tools/upload_cont_med_three_channel.sh` or `tools/upload_cont_med_three_channel.bat`

Each successful firmware compile also saves a timestamped Arduino code copy under `data/arduino_code_snapshots/`. GUI-driven compiles generate that code from the selected signals, highest selected preset rate, and PulseOx phase logic when the `PulseOx` preset is used.

Python student entry points:
- `python/system_check.py`
- `python/run_student_acquisition_gui.py`
