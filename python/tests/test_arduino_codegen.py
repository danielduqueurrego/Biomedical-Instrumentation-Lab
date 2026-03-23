"""Tests for generated Arduino sketch protocol metadata output."""

from __future__ import annotations

from acquisition.arduino_codegen import render_generated_analog_capture_sketch
from acquisition.gui_models import PULSEOX_ROLE_IR, PULSEOX_ROLE_RED, SignalConfiguration


def test_continuous_codegen_includes_expected_metadata_lines() -> None:
    signals = (
        SignalConfiguration(name="EMG A0", preset_name="EMG", analog_port="A0"),
        SignalConfiguration(name="ECG A1", preset_name="ECG", analog_port="A1"),
    )

    sketch = render_generated_analog_capture_sketch(signals, baud_rate=230400)

    assert 'Serial.println("META,acq_class,CONT_HIGH");' in sketch
    assert 'Serial.println("META,fields,t_ms,A0,A1");' in sketch
    assert 'Serial.println("META,selected_ports,A0,A1");' in sketch
    assert "Serial.print(\"DATA,\");" in sketch


def test_pulseox_codegen_includes_phase_and_cycle_metadata_and_sequence() -> None:
    signals = (
        SignalConfiguration(name="Reflective RED", preset_name="PulseOx", analog_port="A0", pulseox_role=PULSEOX_ROLE_RED),
        SignalConfiguration(name="Reflective IR", preset_name="PulseOx", analog_port="A1", pulseox_role=PULSEOX_ROLE_IR),
    )

    sketch = render_generated_analog_capture_sketch(signals, baud_rate=230400)

    assert 'Serial.println("META,acq_class,PHASED_CYCLE");' in sketch
    assert 'Serial.println("META,phase_fields,t_us,cycle_idx,phase,A0,A1");' in sketch
    assert 'Serial.println("META,cycle_fields,t_us,cycle_idx,Reflective RED,Reflective IR");' in sketch
    assert 'Serial.println("META,pulseox_signal_roles,RED,IR");' in sketch
    assert 'Serial.println("META,pulseox_phase_sequence,RED_ON,DARK1,IR_ON,DARK2");' in sketch
    assert "RED_ON -> DARK1 -> IR_ON -> DARK2" in sketch
