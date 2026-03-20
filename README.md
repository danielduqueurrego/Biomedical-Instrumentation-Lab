Biomedical Instrumentation Lab is organized by acquisition pattern first so students and instructors can reuse one software workflow across multiple lab types.

Primary architecture documents:
- `docs/acquisition_architecture.md`
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
- `CONT_MED` three-channel Arduino UNO R4 WiFi demo using the shared `META` and `DATA` packet types

Student setup stays minimal:
- one Conda environment
- `matplotlib` for plotting
- `pyserial` for serial communication
