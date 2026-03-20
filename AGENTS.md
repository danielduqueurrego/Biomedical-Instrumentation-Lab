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
