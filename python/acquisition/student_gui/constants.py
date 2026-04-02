from __future__ import annotations

import re
from pathlib import Path

from acquisition.runtime_paths import session_preset_dir, source_root, gui_session_output_dir

REPO_ROOT = source_root()
DEFAULT_OUTPUT_DIR = gui_session_output_dir()
DEFAULT_SESSION_PRESET_DIR = session_preset_dir()
PLOT_COLORS = ("#0F766E", "#B45309", "#1D4ED8", "#BE123C", "#4338CA", "#047857")
TIMESTAMP_SUFFIX_PATTERN = re.compile(r"_\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}$")
GUI_POLL_INTERVAL_MS = 100
