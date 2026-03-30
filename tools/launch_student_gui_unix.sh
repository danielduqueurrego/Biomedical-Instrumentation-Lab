#!/usr/bin/env bash

# Shared beginner launcher logic for Linux and macOS student GUI wrappers.
set -u

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <launcher_name> <target_script> [args...]"
  exit 2
fi

LAUNCHER_NAME="$1"
TARGET_SCRIPT="$2"
shift 2

PYTHON_DIR="$(cd "$(dirname "$TARGET_SCRIPT")" && pwd)"

print_setup_help() {
  echo "Setup steps:"
  echo "  1) cd \"$PYTHON_DIR\""
  echo "  2) conda env create -f environment.yml"
  echo "  3) Re-run: $LAUNCHER_NAME"
}

find_conda_exe() {
  if command -v conda >/dev/null 2>&1; then
    command -v conda
    return 0
  fi

  local candidates=(
    "$HOME/miniconda3/bin/conda"
    "$HOME/anaconda3/bin/conda"
    "$HOME/mambaforge/bin/conda"
    "/opt/miniconda3/bin/conda"
    "/opt/anaconda3/bin/conda"
  )

  local candidate
  for candidate in "${candidates[@]}"; do
    if [ -x "$candidate" ]; then
      echo "$candidate"
      return 0
    fi
  done

  return 1
}

CONDA_EXE="$(find_conda_exe)"
if [ -z "$CONDA_EXE" ]; then
  echo "ERROR: Conda was not found in PATH or common install locations."
  echo "Install Miniconda or Anaconda, then open a new terminal and try again."
  print_setup_help
  exit 1
fi

# Use the official shell hook so `conda activate` works in non-interactive shells.
eval "$($CONDA_EXE shell.bash hook 2>/dev/null)"
if [ $? -ne 0 ]; then
  echo "ERROR: Failed to initialize Conda shell integration."
  echo "Detected Conda executable: $CONDA_EXE"
  print_setup_help
  exit 1
fi

if ! conda activate biomed-lab >/dev/null 2>&1; then
  echo "ERROR: Conda environment 'biomed-lab' does not exist or failed to activate."
  echo "Create it once with the commands below, then run this launcher again."
  print_setup_help
  exit 1
fi

echo "Launching Student Acquisition GUI..."
python "$TARGET_SCRIPT" "$@"
