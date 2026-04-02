from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


APP_SUPPORT_DIR_NAME = "Biomedical Instrumentation Lab"


def source_root() -> Path:
    """Repository root when running from a source checkout."""
    return Path(__file__).resolve().parents[2]


def running_from_bundle() -> bool:
    """Return True when the app is running from a frozen bundle such as PyInstaller."""
    return bool(getattr(sys, "frozen", False))


def resource_root() -> Path:
    """
    Return the root directory for bundled read-only assets.

    In source checkouts this is the repository root.
    In bundled apps this points to the unpacked application resources.
    """
    if not running_from_bundle():
        return source_root()

    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root)

    return Path(sys.executable).resolve().parent


def writable_app_root() -> Path:
    """
    Return the root directory for writable app data.

    Source checkouts continue to use the repository root so the current developer
    workflow does not change. Bundled apps use a per-user support directory
    because Windows Program Files and macOS .app bundles are not writable.
    """
    override = os.environ.get("BIOMED_LAB_APP_ROOT")
    if override:
        return Path(override).expanduser()

    if not running_from_bundle():
        return source_root()

    home = Path.home()
    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / APP_SUPPORT_DIR_NAME
        return home / "AppData" / "Local" / APP_SUPPORT_DIR_NAME

    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / APP_SUPPORT_DIR_NAME

    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home).expanduser() / APP_SUPPORT_DIR_NAME
    return home / ".local" / "share" / APP_SUPPORT_DIR_NAME


def app_data_root() -> Path:
    return writable_app_root() / "data"


def gui_session_output_dir() -> Path:
    return app_data_root() / "gui_sessions"


def generated_arduino_sketch_dir() -> Path:
    return app_data_root() / "generated_arduino_sketches"


def arduino_code_snapshot_dir() -> Path:
    return app_data_root() / "arduino_code_snapshots"


def cont_med_demo_output_dir() -> Path:
    return app_data_root() / "cont_med" / "three_channel_data_demo"


def bundled_session_preset_dir() -> Path:
    return resource_root() / "python" / "session_presets"


def _seed_session_presets(target_dir: Path) -> None:
    source_dir = bundled_session_preset_dir()
    if not source_dir.is_dir():
        return

    target_dir.mkdir(parents=True, exist_ok=True)
    for source_file in source_dir.glob("*.json"):
        target_file = target_dir / source_file.name
        if target_file.exists():
            continue
        shutil.copy2(source_file, target_file)


def session_preset_dir() -> Path:
    if not running_from_bundle():
        return bundled_session_preset_dir()

    target_dir = writable_app_root() / "session_presets"
    _seed_session_presets(target_dir)
    return target_dir


def resource_path(*parts: str) -> Path:
    return resource_root().joinpath(*parts)
