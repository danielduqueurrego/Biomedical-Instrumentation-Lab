# PulseOx reference sketch

This folder contains a fixed, known-good PulseOx reference sketch for the Arduino UNO R4 WiFi:
- [pulse_ox_reference.ino](./pulse_ox_reference.ino)

## Pin mapping

- `A0 = reflective raw photodiode output`
- `A1 = transmission raw photodiode output`
- `A2 = filtered reflective photodiode output`
- `A3 = filtered transmission photodiode output`
- `D6 = RED LED control`
- `D5 = IR LED control`

## Timing model

- Acquisition class: `PHASED_CYCLE`
- Cycle rate: `100 cycles/s`
- Phase rate: `400 phase samples/s`
- Phase order:
  - `RED_ON`
  - `DARK1`
  - `IR_ON`
  - `DARK2`
- Device timestamp field: `t_us`

Each optical cycle contains four phase captures. One corrected `CYCLE` packet is emitted after `DARK2`.

## Packet fields

Startup metadata:
- `META,lab,PULSEOX_REFERENCE`
- `META,acq_class,PHASED_CYCLE`
- `META,adc_resolution_bits,14`
- `META,cycle_rate_hz,100`
- `META,phase_rate_hz,400`
- `META,selected_ports,A0,A1,A2,A3`
- `META,pulseox_analog_map,reflective_raw=A0,transmission_raw=A1,reflective_filtered=A2,transmission_filtered=A3`
- `META,pulseox_led_pins,IR_D5,RED_D6`
- `META,pulseox_phase_sequence,RED_ON,DARK1,IR_ON,DARK2`
- `META,phase_fields,t_us,cycle_idx,phase,reflective_raw,transmission_raw,reflective_filtered,transmission_filtered`
- `META,cycle_fields,t_us,cycle_idx,reflective_raw_red_corr,reflective_raw_ir_corr,transmission_raw_red_corr,transmission_raw_ir_corr,reflective_filtered_red_corr,reflective_filtered_ir_corr,transmission_filtered_red_corr,transmission_filtered_ir_corr`

Phase packet:
- `PHASE,t_us,cycle_idx,phase,reflective_raw,transmission_raw,reflective_filtered,transmission_filtered`

Cycle packet:
- `CYCLE,t_us,cycle_idx,reflective_raw_red_corr,reflective_raw_ir_corr,transmission_raw_red_corr,transmission_raw_ir_corr,reflective_filtered_red_corr,reflective_filtered_ir_corr,transmission_filtered_red_corr,transmission_filtered_ir_corr`

## Expected output

When used with the current Python GUI:
- the session CSV contains `META`, `PHASE`, and `CYCLE` rows
- the live plot shows the corrected `CYCLE` values
- the saved session CSV keeps the same `row_type` workflow used elsewhere in the repo

## Why this sketch exists

This sketch is for bench validation and known-good checkout.

It differs from the GUI-generated PulseOx firmware in these ways:
- fixed `100 cycles/s` timing instead of deriving timing from the active GUI preset selection
- fixed `PULSEOX_REFERENCE` lab tag instead of `GUI_SELECTED_SIGNALS`
- fixed pin mapping and fixed packet field layout, with no dependence on current GUI state

It intentionally keeps the same PulseOx hardware model and packet semantics as the generated firmware so TAs can compare them directly.

## ADC read strategy

The sketch discards the first ADC read after each channel switch and averages two settled reads per channel. This reduces occasional spike-like artifacts when rapidly scanning `A0` to `A3`.
