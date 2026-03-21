#!/usr/bin/env python3

from pathlib import Path
import sys


PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from acquisition.arduino_cli_wrapper import main


if __name__ == "__main__":
    raise SystemExit(main())
