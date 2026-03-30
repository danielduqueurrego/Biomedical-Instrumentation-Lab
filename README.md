# Open-Source Biomedical Instrumentation Lab

Friendly, student-first tools for **biomedical instrumentation labs** using an Arduino UNO R4 WiFi, a custom lab board, and a Python GUI.

---

## 🚀 Start Here (Students)

1. Install **one Python distribution**: [Anaconda](https://www.anaconda.com/download) (recommended).  
2. Install **Arduino CLI** (or use the setup scripts): [Arduino CLI Docs](https://arduino.github.io/arduino-cli/latest/).  
3. Create the environment and launch the GUI.

```bash
cd python
conda env create -f environment.yml
conda activate biomed-lab
cd ..
./launch_student_doctor_linux.sh
./launch_student_gui_linux.sh
```

> macOS and Windows launchers are also available in the repository root.

---

## ✅ Requirements

### Hardware
- **Arduino UNO R4 WiFi**
- **Biomedical Instrumentation Board** (custom shield):  
  https://oshwlab.com/dd00055/biomedical-instrumentation-board

### Software
- **Python (Conda-based)**: [Anaconda](https://www.anaconda.com/download)
- **Arduino CLI**: [Install guide](https://arduino.github.io/arduino-cli/latest/installation/)
- **Arduino UNO R4 core support**: [Arduino Board Manager](https://docs.arduino.cc/software/ide-v2/tutorials/ide-v2-board-manager/)

---

## 🧠 What this repository includes

- `firmware/` → Arduino firmware organized by acquisition class (`CONT_HIGH`, `CONT_MED`, `PHASED_CYCLE`)
- `python/` → student GUI, acquisition pipeline, logging, and presets
- `docs/` → setup guides, lab guides, protocol docs, validation workflows
- `examples/session_csv/` → example CSV logs for teaching and troubleshooting

---

## 🧪 Supported lab workflows

- **EMG** (`CONT_HIGH`)
- **ECG** (`CONT_MED`)
- **Blood Pressure** (`CONT_MED`)
- **Pulse Oximetry** (`PHASED_CYCLE`)

Shared packet prefixes used across labs:
`META`, `DATA`, `PHASE`, `CYCLE`, `STAT`, `ERR`

---

## 📂 Quick navigation

- Main Python app and setup: [`python/README.md`](python/README.md)
- Firmware overview: [`firmware/cont_high/README.md`](firmware/cont_high/README.md), [`firmware/cont_med/README.md`](firmware/cont_med/README.md), [`firmware/phased_cycle/README.md`](firmware/phased_cycle/README.md)
- Lab guides: [`docs/labs/README.md`](docs/labs/README.md)
- Validation workflow: [`docs/validation/README.md`](docs/validation/README.md)
- Example output format: [`examples/session_csv/README.md`](examples/session_csv/README.md)

---

## 🔐 Licenses

| Area | Typical content | License |
|---|---|---|
| Firmware / Python source | Arduino and Python code | MIT |
| Documentation | Lab and setup docs | CC BY 4.0 |
| Hardware design assets | PCB/schematic assets (where provided) | CERN-OHL-W v2.0 |

See the license files in each folder when present.

---

## 🙌 Contributions

Contributions are welcome from instructors, TAs, and students.

- Open an issue for bug reports or teaching workflow requests
- Open a pull request for improvements
- Keep changes simple, well-documented, and student-friendly
