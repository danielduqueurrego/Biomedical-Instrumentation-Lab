# PulseOx Reference Sketch

> Fixed, known-good PulseOx reference sketch for the Arduino UNO R4 WiFi.

Use this sketch when you want a committed PulseOx implementation that matches the current board model and shared protocol exactly.

---

## Quick Reference

| Item | Current value |
| --- | --- |
| Acquisition class | `PHASED_CYCLE` |
| Cycle rate | `100 cycles/s` |
| Phase rate | `400 phase samples/s` |
| Timestamp field | `t_us` |
| ADC setting | `analogReadResolution(14)` |

---

## Pin Mapping

- `A0 = reflective raw photodiode output`
- `A1 = transmission raw photodiode output`
- `A2 = filtered reflective photodiode output`
- `A3 = filtered transmission photodiode output`
- `D6 = RED LED control`
- `D5 = IR LED control`

Important model rule:

- red versus IR is determined by phase timing, not by separate analog outputs

---

## Timing Model

Phase order:

- `RED_ON`
- `DARK1`
- `IR_ON`
- `DARK2`

Each optical cycle contains four phase captures. One corrected `CYCLE` packet is emitted after `DARK2`.

---

## Packet Fields

Startup metadata includes:

- `META,lab,PULSEOX_REFERENCE`
- `META,acq_class,PHASED_CYCLE`
- `META,adc_resolution_bits,14`
- `META,cycle_rate_hz,100`
- `META,phase_rate_hz,400`
- `META,selected_ports,A0,A1,A2,A3`
- `META,pulseox_analog_map,reflective_raw=A0,transmission_raw=A1,reflective_filtered=A2,transmission_filtered=A3`
- `META,pulseox_led_pins,IR_D5,RED_D6`
- `META,pulseox_phase_sequence,RED_ON,DARK1,IR_ON,DARK2`

Raw phase rows:

- `PHASE,t_us,cycle_idx,phase,reflective_raw,transmission_raw,reflective_filtered,transmission_filtered`

Corrected cycle rows:

- `CYCLE,t_us,cycle_idx,reflective_raw_red_corr,reflective_raw_ir_corr,transmission_raw_red_corr,transmission_raw_ir_corr,reflective_filtered_red_corr,reflective_filtered_ir_corr,transmission_filtered_red_corr,transmission_filtered_ir_corr`

---

## How It Differs From Generated Firmware

This committed sketch is fixed and known-good.

The GUI-generated PulseOx firmware follows the same hardware model and packet semantics, but it is generated at runtime from the current student configuration and still saves a compiled code copy under `data/arduino_code_snapshots/`.

---

## Expected Output

During a normal run, students should expect:

- `META` startup rows
- `PHASE` rows for each phase
- `CYCLE` rows for corrected cycle values

In the GUI session CSV, those rows are stored together in one file and filtered by `row_type`.

---

## See Also

- [PulseOx lab guide](../../../../docs/labs/pulse_ox.md)
- [Generated firmware workflow](../../../../docs/generated_firmware_workflow.md)
- [Serial protocol](../../../../docs/serial_protocol.md)
