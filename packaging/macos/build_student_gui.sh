#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENTRY_SCRIPT="$REPO_ROOT/python/run_student_acquisition_gui.py"

echo "Building macOS student GUI app bundle with PyInstaller..."

cd "$REPO_ROOT"
pyinstaller \
  --noconfirm \
  --clean \
  --onedir \
  --windowed \
  --name "Biomedical Instrumentation Lab" \
  --paths "$REPO_ROOT/python" \
  --add-data "$REPO_ROOT/firmware:firmware" \
  --add-data "$REPO_ROOT/python/session_presets:python/session_presets" \
  --hidden-import matplotlib.backends.backend_tkagg \
  --hidden-import serial.tools.list_ports \
  "$ENTRY_SCRIPT"

echo
echo "Build finished."
echo "App bundle:"
echo "  dist/Biomedical Instrumentation Lab.app"
