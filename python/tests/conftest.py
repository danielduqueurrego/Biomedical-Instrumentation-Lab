"""Shared pytest fixtures with representative serial protocol lines."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import enum
import pytest

if not hasattr(enum, "StrEnum"):
    class _CompatStrEnum(str, enum.Enum):
        """Compatibility shim for Python versions below 3.11."""

    enum.StrEnum = _CompatStrEnum


REPO_ROOT = Path(__file__).resolve().parents[2]
ACQUISITION_DIR = REPO_ROOT / "python" / "acquisition"


def _load_acquisition_submodule(module_name: str) -> None:
    """Load acquisition submodules directly from file paths for Python 3.10 test environments."""
    full_name = f"acquisition.{module_name}"
    if full_name in sys.modules:
        return

    module_path = ACQUISITION_DIR / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(full_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module {full_name} from {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)


def _bootstrap_acquisition_package() -> None:
    """Provide a lightweight package shell so imports skip acquisition/__init__.py."""
    if "acquisition" not in sys.modules:
        package = types.ModuleType("acquisition")
        package.__path__ = [str(ACQUISITION_DIR)]
        sys.modules["acquisition"] = package

    # Load dependencies in import order used by modules under test.
    for module_name in ("protocol", "presets", "gui_models", "arduino_codegen"):
        _load_acquisition_submodule(module_name)


_bootstrap_acquisition_package()


@pytest.fixture
def host_timestamp() -> tuple[str, float]:
    """Stable host timestamp tuple used by packet parser tests."""
    return "2026-03-23T12:00:00Z", 1774267200.0


@pytest.fixture
def protocol_lines() -> dict[str, str]:
    """Representative lines based on docs/serial_protocol.md examples."""
    return {
        "meta_fields": "META,fields,t_ms,A0,A1,A2",
        "data_valid": "DATA,1523,512,487,530",
        "data_non_integer": "DATA,1523,512,bad,530",
        "phase_valid": "PHASE,125000,312,RED_ON,1842,1760,1901",
        "phase_unknown": "PHASE,125000,312,BLUE_ON,1842,1760,1901",
        "cycle_valid": "CYCLE,127550,312,1721,1645,1688",
        "cycle_bad_value": "CYCLE,127550,312,1721,bad,1688",
        "unknown_prefix": "BOGUS,1,2,3",
        "short_data": "DATA,1523",
    }
