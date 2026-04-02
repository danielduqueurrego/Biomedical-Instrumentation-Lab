# Desktop Packaging

This folder contains the first packaging scaffold for the student GUI.

The current goal is:

- Windows: build a bundled `.exe` directory with PyInstaller and install it under `Program Files`
- macOS: build a `.app` bundle with PyInstaller

This packaging work keeps student runtime behavior separate from source-checkout behavior:

- source checkout: generated sketches, snapshots, and default session output stay inside the repo
- bundled app: writable files move to a per-user support folder
- bundled app: read-only presets and firmware are loaded from packaged resources

## Current status

Implemented in this branch:

- runtime path detection for source checkout vs bundled app
- packaged-app user data directories
- preset seeding for bundled apps
- Windows PyInstaller build script
- Windows Inno Setup installer script
- bundled Arduino CLI payload for the Windows installer
- optional Arduino CLI removal during Windows uninstall
- macOS PyInstaller build script

Still needed later:

- code signing on Windows
- notarization/signing on macOS
- DMG or PKG generation for macOS distribution
- CI packaging jobs and release artifacts

## Prerequisites

Builder machines need:

- Python 3.11
- `pyinstaller`
- platform-native tooling
  - Windows installer: Inno Setup 6
  - macOS distribution: optional DMG/PKG tooling if you want a polished installer later

Install PyInstaller in your builder environment with:

```bash
python -m pip install pyinstaller
```

## Windows build

From the repository root in PowerShell:

```powershell
.\packaging\windows\build_student_gui.ps1
```

The build script looks for `arduino-cli.exe` in:

- `C:\Program Files\Arduino CLI`
- `C:\Program Files (x86)\Arduino CLI`
- `C:\arduino-cli`
- `PATH`

If Arduino CLI is found, the script refreshes the installer payload from that executable. If it is not found, the script clears any stale bundled payload and continues building the GUI bundle without Arduino CLI.

That creates:

- `dist\Biomedical Instrumentation Lab\Biomedical Instrumentation Lab.exe`

To create an installer for `Program Files`, open Inno Setup and build:

- `packaging\windows\student_gui_installer.iss`

The installer is configured for:

- install folder: `C:\Program Files\Biomedical Instrumentation Lab`
- Start Menu shortcut
- optional desktop shortcut
- optional bundled Arduino CLI install to `C:\Program Files\Arduino CLI`
- machine `PATH` and `ARDUINO_CLI` registration when Arduino CLI is installed
- uninstall prompt that asks whether to also remove the bundled Arduino CLI

## macOS build

From the repository root:

```bash
chmod +x packaging/macos/build_student_gui.sh
./packaging/macos/build_student_gui.sh
```

That creates:

- `dist/Biomedical Instrumentation Lab.app`

## Arduino CLI note

The Windows installer can bundle `arduino-cli` for student machines, so compile/upload works without a separate manual install.

On uninstall, the app is removed first, and the uninstaller then asks whether the bundled Arduino CLI should also be removed. If you keep it, the machine `PATH` entry and `ARDUINO_CLI` variable stay in place for future use.

For automated uninstall testing, the uninstaller also supports:

- `/KEEPARDUINOCLI`
- `/REMOVEARDUINOCLI`
