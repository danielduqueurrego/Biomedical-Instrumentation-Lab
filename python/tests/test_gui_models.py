"""Tests for GUI signal configuration validation rules."""

from __future__ import annotations

import pytest

from acquisition.gui_models import (
    SignalConfiguration,
    validate_signal_configurations,
)


def test_validate_signal_configurations_accepts_fixed_pulseox_mapping() -> None:
    signals = (
        SignalConfiguration(name="Reflective raw", preset_name="PulseOx", analog_port="A0"),
        SignalConfiguration(name="Transmission raw", preset_name="PulseOx", analog_port="A1"),
        SignalConfiguration(name="Reflective filtered", preset_name="PulseOx", analog_port="A2"),
        SignalConfiguration(name="Transmission filtered", preset_name="PulseOx", analog_port="A3"),
    )

    validate_signal_configurations(signals)


def test_validate_signal_configurations_rejects_wrong_pulseox_port_order() -> None:
    signals = (
        SignalConfiguration(name="Reflective raw", preset_name="PulseOx", analog_port="A1"),
        SignalConfiguration(name="Transmission raw", preset_name="PulseOx", analog_port="A0"),
        SignalConfiguration(name="Reflective filtered", preset_name="PulseOx", analog_port="A2"),
        SignalConfiguration(name="Transmission filtered", preset_name="PulseOx", analog_port="A3"),
    )

    with pytest.raises(ValueError, match="must keep the analog ports in this order"):
        validate_signal_configurations(signals)


def test_validate_signal_configurations_rejects_mixed_pulseox_and_continuous_presets() -> None:
    signals = (
        SignalConfiguration(name="Reflective raw", preset_name="PulseOx", analog_port="A0"),
        SignalConfiguration(name="EMG Signal", preset_name="EMG", analog_port="A1"),
    )

    with pytest.raises(ValueError, match="Do not mix PulseOx signals"):
        validate_signal_configurations(signals)
