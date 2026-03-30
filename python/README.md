# Python Tools and Student GUI

This folder contains the student-facing GUI and shared acquisition pipeline.

## Requirements
- [Anaconda (recommended)](https://www.anaconda.com/download)
- [Arduino CLI](https://arduino.github.io/arduino-cli/latest/installation/)

## Setup
```bash
cd python
conda env create -f environment.yml
conda activate biomed-lab
cd ..
```

## Launch
From repository root:
- Linux: `./launch_student_gui_linux.sh`
- macOS: `./launch_student_gui_macos.command`
- Windows: `launch_student_gui_windows.bat`

## What the GUI supports
- board and port selection
- optional firmware compile/upload
- 1–6 active signals with names/presets
- live plotting
- session CSV logging
- load/save preset JSON files

## Key folders
- `acquisition/` shared protocol, serial, logging, plotting
- `acquisition/student_gui/` modular Tkinter GUI
- `apps/` student app entry points
- `session_presets/` lab preset JSON files

## Related docs
- [Main README](../README.md)
- [Student setup guide](../docs/student_setup.md)
- [Session presets README](./session_presets/README.md)
