from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "gui_sessions"
DEFAULT_SESSION_PRESET_DIR = REPO_ROOT / "python" / "session_presets"
PLOT_COLORS = ("#0F766E", "#B45309", "#1D4ED8", "#BE123C", "#4338CA", "#047857")
TIMESTAMP_SUFFIX_PATTERN = re.compile(r"_\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}$")
GUI_POLL_INTERVAL_MS = 100
