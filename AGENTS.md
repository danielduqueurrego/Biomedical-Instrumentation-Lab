# Biomedical-Instrumentation-Lab

## Project goal
This repository contains Arduino and Python code for biomedical instrumentation laboratory boards.

## Main acquisition classes
1. Continuous streaming labs
   - Examples: EMG, ECG
   - Stream timestamped analog samples over serial

2. Sequenced optical labs
   - Example: pulse oximetry
   - Acquisition phases:
     - RED_ON
     - DARK1
     - IR_ON
     - DARK2

## Coding rules
- Keep code simple and heavily commented for students.
- Prefer modular files over one large script.
- Do not add unnecessary dependencies.
- Keep Arduino and Python code separated cleanly.
- Use human-readable serial output first.
- Always explain assumptions before major refactors.
- For Python, prioritize reliability of logging over plotting speed.
- For plotting, avoid redrawing more often than needed.
- Preserve a shared serial protocol document in docs/serial_protocol.md.

## Safety and workflow
- Make small, high-confidence changes.
- After each meaningful change, suggest a git commit message.
- Do not invent hardware details that are not written in the docs.

## Student installation and usability priority
This project must be as easy as possible for undergraduate students to install and use.

### Requirements
- Minimize required software installations.
- Prefer a single Python distribution for students, ideally Anaconda or another free Conda-based option.
- Avoid requiring students to install multiple tools, IDEs, package managers, or complex drivers unless absolutely necessary.
- The student workflow should be:
  1. install the required Python distribution,
  2. create or load one environment,
  3. run one command or double-click one launcher script.

### Python dependency policy
- Keep dependencies minimal.
- Prefer widely used, stable, free packages.
- Avoid unnecessary GUI frameworks or heavy libraries unless they clearly improve usability.
- Do not introduce dependencies that are difficult to install on Windows or macOS.

### Deliverable expectations
- Provide an environment file for setup.
- Provide a simple launch script for students.
- Provide clear setup instructions written for beginners.
- Prefer one main application entry point per lab.
- Design the software so students can use it without editing source code.

### Usability goal
The final student-facing workflow should feel close to:
- connect Arduino,
- open terminal or launcher,
- run one command,
- see live plots,
- save data automatically.

## Architecture rule
Organize the repository by acquisition pattern, not only by sensor name.

Supported acquisition classes:
- CONT_HIGH: high-rate continuous waveform acquisition
- CONT_MED: medium-rate continuous waveform acquisition
- PHASED_CYCLE: multi-phase acquisition where one final sample is reconstructed from several timed phases
- PROC_CONT: continuous acquisition with procedure/state events

Every lab must declare:
- acquisition class
- default sampling rate
- packet types used
- fields emitted
- optional stage names
- plotting defaults

All serial packets must use a shared protocol with packet prefixes such as:
META, DATA, PHASE, CYCLE, EVENT, STAT, ERR

Keep student installation simple:
- minimal dependencies
- one Conda environment
- beginner-friendly run commands
- no need for students to edit source code

## Student usability requirement
This project must be extremely easy for students to install and use.

Priorities:
- minimize required software
- prefer one Conda-based Python environment
- use Arduino CLI behind scripts and GUI instead of exposing raw commands to students
- support Windows, macOS, and Linux
- provide setup documentation for all three OSes
- provide launcher scripts for all three OSes
- avoid unnecessary dependencies

## GUI requirement
The project must include a Python GUI for students.

The GUI should allow:
- selecting serial port and board
- optionally compiling/uploading firmware through Arduino CLI
- choosing how many signals are active
- assigning each signal a name and a preset/type
- showing the predefined sampling parameters for each signal type
- selecting save folder and filename
- starting/stopping acquisition
- displaying live plots
- logging data to file

Use a simple cross-platform GUI approach first, prioritizing low installation burden and maintainability.
Prefer tkinter/ttk for v1 unless a stronger dependency is clearly justified.
