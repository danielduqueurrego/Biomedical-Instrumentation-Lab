"""Tests for source-vs-bundled runtime path resolution."""

from __future__ import annotations

from pathlib import Path

from acquisition import runtime_paths
from acquisition.student_gui import preset_io


def test_writable_app_root_uses_source_root_when_not_frozen(monkeypatch) -> None:
    monkeypatch.delenv("BIOMED_LAB_APP_ROOT", raising=False)
    monkeypatch.delattr(runtime_paths.sys, "frozen", raising=False)
    monkeypatch.delattr(runtime_paths.sys, "_MEIPASS", raising=False)

    assert runtime_paths.writable_app_root() == runtime_paths.source_root()


def test_session_preset_dir_seeds_bundled_json_files(monkeypatch, tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundle"
    bundled_preset_dir = bundle_root / "python" / "session_presets"
    bundled_preset_dir.mkdir(parents=True)
    (bundled_preset_dir / "ecg.json").write_text('{"preset_name": "ECG"}\n', encoding="utf-8")
    (bundled_preset_dir / "emg.json").write_text('{"preset_name": "EMG"}\n', encoding="utf-8")

    app_root = tmp_path / "user-data"
    monkeypatch.setenv("BIOMED_LAB_APP_ROOT", str(app_root))
    monkeypatch.setattr(runtime_paths.sys, "frozen", True, raising=False)
    monkeypatch.setattr(runtime_paths.sys, "_MEIPASS", str(bundle_root), raising=False)

    resolved_dir = runtime_paths.session_preset_dir()

    assert resolved_dir == app_root / "session_presets"
    assert (resolved_dir / "ecg.json").is_file()
    assert (resolved_dir / "emg.json").is_file()


def test_relative_preset_paths_resolve_inside_writable_app_root_when_bundled(monkeypatch, tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundle"
    bundle_root.mkdir()
    app_root = tmp_path / "portable-user-data"
    monkeypatch.setenv("BIOMED_LAB_APP_ROOT", str(app_root))
    monkeypatch.setattr(runtime_paths.sys, "frozen", True, raising=False)
    monkeypatch.setattr(runtime_paths.sys, "_MEIPASS", str(bundle_root), raising=False)

    resolved = preset_io.resolve_preset_path("data/gui_sessions")

    assert resolved == app_root / "data" / "gui_sessions"
