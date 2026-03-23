#!/usr/bin/env bash

# Beginner launcher for Linux students.
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$SCRIPT_DIR/python"
TARGET_SCRIPT="$PYTHON_DIR/run_student_acquisition_gui.py"

print_setup_help() {
  echo "Setup steps:"
  echo "  1) cd \"$PYTHON_DIR\""
  echo "  2) conda env create -f environment.yml"
  echo "  3) Re-run: ./launch_student_gui_linux.sh"
}

if ! command -v conda >/dev/null 2>&1; then
  echo "ERROR: Conda was not found in your terminal PATH."
  echo "Install Miniconda or Anaconda, then open a new terminal and try again."
  print_setup_help
  exit 1
fi

CONDA_BASE="$(conda info --base 2>/dev/null)"
if [ -z "$CONDA_BASE" ] || [ ! -f "$CONDA_BASE/etc/profile.d/conda.sh" ]; then
  echo "ERROR: Could not find conda activation script at: $CONDA_BASE/etc/profile.d/conda.sh"
  echo "Please verify your Conda installation, then try again."
  print_setup_help
  exit 1
fi

# shellcheck source=/dev/null
source "$CONDA_BASE/etc/profile.d/conda.sh"

if ! conda activate biomed-lab >/dev/null 2>&1; then
  echo "ERROR: Conda environment 'biomed-lab' does not exist or failed to activate."
  echo "Create it once with the commands below, then run this launcher again."
  print_setup_help
  exit 1
fi

echo "Launching Student Acquisition GUI..."
python "$TARGET_SCRIPT" "$@"
