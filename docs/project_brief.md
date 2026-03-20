# Project brief

This repository supports biomedical instrumentation labs built around Arduino boards and Python desktop tools.

## Initial targets
- Arduino UNO R4 WiFi firmware
- Python live plotting
- Python CSV logging
- Reusable parsers and protocol helpers

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

## First milestone
Create one working end-to-end continuous-stream example and one pulse-ox state-machine example.

## Constraints
- Keep the stack free and student-friendly
- Prioritize clarity and maintainability
- Design the Python side so it can parse multiple packet types
