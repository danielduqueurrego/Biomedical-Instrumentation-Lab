"""Tests for generated Arduino sketch protocol metadata output."""

from __future__ import annotations

from acquisition.arduino_codegen import render_generated_analog_capture_sketch
from acquisition.gui_models import SignalConfiguration
from acquisition.protocol import PULSEOX_CYCLE_VALUE_FIELDS, PULSEOX_PHASE_VALUE_FIELDS


def test_continuous_codegen_includes_expected_metadata_lines() -> None:
    signals = (
        SignalConfiguration(name="EMG A0", preset_name="EMG", analog_port="A0"),
        SignalConfiguration(name="ECG A1", preset_name="ECG", analog_port="A1"),
    )

    sketch = render_generated_analog_capture_sketch(signals, baud_rate=230400)

    assert 'Serial.println("META,acq_class,CONT_HIGH");' in sketch
    assert 'Serial.println("META,fields,t_us,A0,A1");' in sketch
    assert 'Serial.println("META,adc_resolution_bits,14");' in sketch
    assert 'Serial.println("META,selected_ports,A0,A1");' in sketch
    assert "analogReadResolution(14);" in sketch
    assert "Serial.print(\"DATA,\");" in sketch


def test_pulseox_codegen_includes_phase_and_cycle_metadata_and_sequence() -> None:
    signals = (
        SignalConfiguration(name="Reflective raw", preset_name="PulseOx", analog_port="A0"),
        SignalConfiguration(name="Transmission raw", preset_name="PulseOx", analog_port="A1"),
        SignalConfiguration(name="Reflective filtered", preset_name="PulseOx", analog_port="A2"),
        SignalConfiguration(name="Transmission filtered", preset_name="PulseOx", analog_port="A3"),
    )

    sketch = render_generated_analog_capture_sketch(signals, baud_rate=230400)

    assert 'Serial.println("META,acq_class,PHASED_CYCLE");' in sketch
    assert (
        f'Serial.println("META,phase_fields,t_us,cycle_idx,phase,{",".join(PULSEOX_PHASE_VALUE_FIELDS)}");'
        in sketch
    )
    assert (
        f'Serial.println("META,cycle_fields,t_us,cycle_idx,{",".join(PULSEOX_CYCLE_VALUE_FIELDS)}");'
        in sketch
    )
    assert 'Serial.println("META,adc_resolution_bits,14");' in sketch
    assert 'Serial.println("META,pulseox_phase_sequence,RED_ON,DARK1,IR_ON,DARK2");' in sketch
    assert "analogReadResolution(14);" in sketch
    assert "int readSettledPulseOxChannel(int analogPin)" in sketch
    assert "phaseSamples[currentPhase][index] = readSettledPulseOxChannel(ANALOG_INPUT_PINS[index]);" in sketch
    assert "RED_ON -> DARK1 -> IR_ON -> DARK2" in sketch
