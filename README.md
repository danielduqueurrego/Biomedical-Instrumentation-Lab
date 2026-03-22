Biomedical Instrumentation Lab is organized by acquisition pattern first so students and instructors can reuse one software workflow across multiple lab types.

Primary architecture documents:
- `docs/acquisition_architecture.md`
- `docs/arduino_cli_setup.md`
- `docs/student_setup.md`
- `docs/sampling_strategy.md`
- `docs/serial_protocol.md`

Top-level structure:
- `firmware/cont_high`: high-rate continuous waveform sketches such as EMG
- `firmware/cont_med`: medium-rate continuous waveform sketches such as ECG and classroom demos
- `firmware/phased_cycle`: multi-phase optical acquisition sketches such as pulse oximetry
- `firmware/proc_cont`: procedure-driven continuous sketches such as blood pressure
- `python/acquisition`: shared Python protocol, preset, serial, logging, and plotting helpers
- `python/apps`: student-facing Python apps built on the shared acquisition helpers

Current implemented baseline:
- `CONT_MED` Arduino UNO R4 WiFi analog-bank demo using the shared `META` and `DATA` packet types
- first Tkinter GUI foundation for student acquisition setup, lab-profile loading, and live plotting

Student setup stays minimal:
- one Conda environment
- `matplotlib` for plotting
- `pyserial` for serial communication
- Arduino CLI for command-line firmware compile and upload

Arduino CLI helper scripts:
- `tools/setup_arduino_cli.sh` or `tools/setup_arduino_cli.bat`
- `tools/upload_cont_med_three_channel.sh` or `tools/upload_cont_med_three_channel.bat`

Each successful firmware compile also saves a timestamped copy of the Arduino sketch source under `data/arduino_code_snapshots/`.

Python student entry points:
- `python/system_check.py`
- `python/run_student_acquisition_gui.py`
