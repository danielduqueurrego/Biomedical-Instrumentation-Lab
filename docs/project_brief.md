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
Examples: EMG, ECG, Blood Pressure

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

## Current implementation direction

The repository currently supports:
- one working end-to-end `CONT_MED` example
- generated firmware for student GUI workflows
- true `PHASED_CYCLE` PulseOx support using `PHASE` and `CYCLE` packets
- a shared serial protocol across all supported acquisition classes

## Constraints
- Keep the stack free and student-friendly
- Prioritize clarity and maintainability
- Design the Python side so it can parse multiple packet types
- Organize the repository by acquisition pattern first

## Student deployment constraint

A major goal of this repository is student usability.

The software must be designed so that students can install and run it with minimal setup burden. Prefer a single free software ecosystem for the computer side, ideally a Conda-based Python installation. Avoid requiring multiple separate software tools unless absolutely necessary.

The preferred student setup is:
- Arduino CLI behind scripts or the GUI for firmware upload
- one Conda-based Python installation for acquisition software
- one environment file
- one launch command or launcher script

The project should prioritize:
- simple installation
- simple launching
- minimal dependencies
- beginner-friendly documentation
- robust behavior even if students are not experienced programmers
