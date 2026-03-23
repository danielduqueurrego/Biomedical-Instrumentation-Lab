"""Tests for GUI signal configuration validation rules."""

from __future__ import annotations

import pytest

from acquisition.gui_models import (
    PULSEOX_ROLE_AUTO,
    PULSEOX_ROLE_IR,
    PULSEOX_ROLE_RED,
    SignalConfiguration,
    validate_signal_configurations,
)


def test_validate_signal_configurations_accepts_all_pulseox_with_explicit_roles() -> None:
    signals = (
        SignalConfiguration(name="Red Signal", preset_name="PulseOx", analog_port="A0", pulseox_role=PULSEOX_ROLE_RED),
        SignalConfiguration(name="IR Signal", preset_name="PulseOx", analog_port="A1", pulseox_role=PULSEOX_ROLE_IR),
    )

    validate_signal_configurations(signals)


def test_validate_signal_configurations_rejects_pulseox_auto_role() -> None:
    signals = (
        SignalConfiguration(name="Red Signal", preset_name="PulseOx", analog_port="A0", pulseox_role=PULSEOX_ROLE_AUTO),
    )

    with pytest.raises(ValueError, match="needs a RED or IR PulseOx role"):
        validate_signal_configurations(signals)


def test_validate_signal_configurations_rejects_mixed_pulseox_and_continuous_presets() -> None:
    signals = (
        SignalConfiguration(name="Red Signal", preset_name="PulseOx", analog_port="A0", pulseox_role=PULSEOX_ROLE_RED),
        SignalConfiguration(name="EMG Signal", preset_name="EMG", analog_port="A1", pulseox_role=PULSEOX_ROLE_AUTO),
    )

    with pytest.raises(ValueError, match="Do not mix PHASED_CYCLE signals"):
        validate_signal_configurations(signals)
