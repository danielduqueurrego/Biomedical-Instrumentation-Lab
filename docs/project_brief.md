# Project brief

This repository supports biomedical instrumentation labs built around Arduino boards and Python desktop tools.

## Initial targets
- Arduino UNO R4 WiFi firmware
- Python live plotting
- Python CSV logging
- Reusable parsers and protocol helpers
- Pattern-first repository architecture

## Lab types

### 1. Continuous stream labs
Examples: EMG, ECG

Expected output:
- timestamp
- one or more analog channels

### 2. Sequenced pulse-oximetry lab
Expected acquisition stages:
- Red LED on
- All LEDs off
- IR LED on
- All LEDs off

The software must support:
- raw phase logging
- reconstructed cycle logging
- live plotting
- CSV export

### 3. Procedure-driven continuous labs
Examples: blood pressure

Expected output:
- continuous waveform samples
- explicit stage events
- summary statistics when needed

## First milestone
Create one working end-to-end `CONT_MED` example, define the shared serial protocol, and scaffold the repository for `CONT_HIGH`, `PHASED_CYCLE`, and `PROC_CONT`.

## Constraints
- Keep the stack free and student-friendly
- Prioritize clarity and maintainability
- Design the Python side so it can parse multiple packet types
- Organize the repository by acquisition pattern first

## Student deployment constraint

A major goal of this repository is student usability.

The software must be designed so that students can install and run it with minimal setup burden. Prefer a single free software ecosystem for the computer side, ideally a Conda-based Python installation. Avoid requiring multiple separate software tools unless absolutely necessary.

The preferred student setup is:
- Arduino IDE for uploading firmware
- one Conda-based Python installation for acquisition software
- one environment file
- one launch command or launcher script

The project should prioritize:
- simple installation
- simple launching
- minimal dependencies
- beginner-friendly documentation
- robust behavior even if students are not experienced programmers
