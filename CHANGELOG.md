# Changelog

All notable changes to the Biomedical Instrumentation Lab are recorded here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
Firmware versions are tracked per sketch via the `META,firmware_version,N` packet emitted at startup.

---

## [Unreleased]

### Added

- **ECG reference sketch** (`firmware/cont_med/uno_r4_wifi/ecg_reference/`) — named `CONT_MED` sketch at 500 Hz with labeled channels `ECG_A0`, `ECG_A1`, `ECG_A2`.
- **Blood Pressure reference sketch** (`firmware/cont_med/uno_r4_wifi/blood_pressure_reference/`) — named `CONT_MED` sketch at 200 Hz sampling `BP_A0`.
- **`META,firmware_version,N` packet** in all reference sketches — lets the Python host warn students if firmware and software versions do not match.
- **`compile-ecg-reference` and `upload-ecg-reference` CLI commands** in `tools/arduino_cli.py` and `arduino_cli_wrapper.py`.
- **`compile-bp-reference` and `upload-bp-reference` CLI commands** in `tools/arduino_cli.py` and `arduino_cli_wrapper.py`.
- **Upload helper scripts** `tools/upload_cont_med_ecg_reference.sh/.bat` and `tools/upload_cont_med_blood_pressure_reference.sh/.bat`.
- **`pytest-cov`** added to `python/environment-dev.yml` for coverage reporting during development.

### Changed

- `firmware/cont_med/README.md` updated to list all three committed CONT_MED reference sketches with descriptions and per-sketch upload commands.

---

## Serial Protocol

Current serial protocol version: **v4**  
See [docs/serial_protocol.md](docs/serial_protocol.md) for the full specification.

### Firmware version history

| Sketch | Version | Notes |
| --- | --- | --- |
| `emg_high_rate_reference` | 1 | Initial versioned release |
| `emg_four_channel_demo` | 1 | Initial versioned release |
| `three_channel_data_demo` | 1 | Initial versioned release |
| `ecg_reference` | 1 | New sketch |
| `blood_pressure_reference` | 1 | New sketch |
| `pulse_ox_reference` | 1 | Initial versioned release |
