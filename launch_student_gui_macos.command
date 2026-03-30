#!/usr/bin/env bash

# Beginner launcher for macOS students.
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_SCRIPT="$SCRIPT_DIR/python/run_student_acquisition_gui.py"
UNIX_LAUNCHER="$SCRIPT_DIR/tools/launch_student_gui_unix.sh"

exec "$UNIX_LAUNCHER" "./launch_student_gui_macos.command" "$TARGET_SCRIPT" "$@"
