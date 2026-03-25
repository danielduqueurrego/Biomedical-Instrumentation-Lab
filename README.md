# Biomedical Instrumentation Lab

An open, teaching-focused platform for **biomedical instrumentation laboratories** built around a custom PCB, Arduino-based acquisition, and a student-friendly Python GUI.

This repository brings together the pieces needed to run hands-on labs in signals and instrumentation such as:

- **EMG**
- **ECG**
- **Pulse oximetry**
- **Blood pressure**
- other analog and phased-cycle biomedical sensing activities

## Why this project exists

Biomedical instrumentation is often taught with a gap between theory and practice: students learn signal conditioning, filtering, sampling, and physiological measurement concepts, but may not always get a reusable, transparent, and low-cost platform they can explore themselves.

This project was created to help close that gap by providing:

- a **custom educational PCB**
- **open firmware workflows**
- a **cross-platform acquisition GUI**
- reusable lab presets and examples
- a structure that supports both **teaching** and **iteration**

The goal is to make biomedical instrumentation more accessible, reproducible, and hands-on for students and instructors.

## What this repository includes

- **Hardware-oriented workflows** for a biomedical instrumentation board
- **Arduino UNO R4 WiFi firmware** for multiple acquisition patterns
- a **Python GUI** for student data collection
- support for:
  - continuous high-rate acquisition
  - continuous medium-rate acquisition
  - phased-cycle optical acquisition
- example CSV outputs
- validation checklists
- student setup documentation
- tools for compile/upload workflows using **Arduino CLI**

## Current PCB design

The current board design is published on OSHWLab:

**PCB project:** [Biomedical Instrumentation Board](https://oshwlab.com/dd00055/biomedical-instrumentation-board)

This board is intended as the hardware foundation for the labs in this repository and is being developed as an educational platform for biosignal acquisition and analysis.

## Project philosophy

This repository is organized by **acquisition pattern first**, not only by signal type.  
That allows one software workflow to be reused across multiple labs.

Current acquisition classes include:

- **CONT_HIGH** – high-rate continuous waveform acquisition
- **CONT_MED** – medium-rate continuous waveform acquisition
- **PHASED_CYCLE** – multi-phase acquisition such as pulse oximetry

This makes it easier to extend the platform to new labs while keeping the student experience consistent.

## Student workflow

The intended student workflow is:

1. connect the board
2. launch the GUI
3. select a lab preset
4. choose a save folder
5. upload firmware if needed
6. start acquisition
7. save a single CSV session file

The repository is designed to keep installation simple by using:

- **Conda** for the Python environment
- **Arduino CLI** for compile/upload workflows
- a **Python GUI** for routine student use

## Repository structure

```text
docs/        Documentation, lab guides, setup, validation
examples/    Example session CSV files and reference outputs
firmware/    Arduino firmware organized by acquisition class
python/      Acquisition code, GUI, presets, and utilities
tests/       Automated tests
tools/       Arduino CLI setup/upload helper scripts
