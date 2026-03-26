# Serial Protocol v4

> Shared ASCII CSV serial protocol for all acquisition classes in this repository.

Use this document when you are implementing firmware, parsing logs, or checking whether a session CSV matches the current repo expectations.

---

## Start Here

Current protocol rules:

- transport: USB serial
- default baud: `230400`
- every device packet is a newline-terminated ASCII CSV string
- field `0` is always the packet prefix
- no debug text should appear during acquisition
- Python loggers add host timestamps when a line is received
- device packets should include a device timestamp whenever timing matters

The current packet family is:

- `META`
- `DATA`
- `PHASE`
- `CYCLE`
- `STAT`
- `ERR`

---

## Quick Timing Rules

| Acquisition class | Main data packet | Timing field |
| --- | --- | --- |
| `CONT_HIGH` | `DATA` | `t_us` |
| `CONT_MED` | `DATA` | `t_ms` |
| `PHASED_CYCLE` | `PHASE`, `CYCLE` | `t_us` |

---

## Packet Reference

### `META`

Use `META` for startup metadata and field-layout declarations.

Format:

`META,key,value1,value2,...`

Current examples:

- `META,lab,GUI_SELECTED_SIGNALS`
- `META,acq_class,CONT_HIGH`
- `META,rate_hz,2000`
- `META,adc_resolution_bits,14`
- `META,fields,t_us,A0,A1,A2,A3`
- `META,acq_class,CONT_MED`
- `META,rate_hz,200`
- `META,fields,t_ms,A0,A1,A2,A3`
- `META,selected_ports,A0,A1,A2,A3`
- `META,acq_class,PHASED_CYCLE`
- `META,cycle_rate_hz,100`
- `META,phase_rate_hz,400`
- `META,phase_fields,t_us,cycle_idx,phase,reflective_raw,transmission_raw,reflective_filtered,transmission_filtered`
- `META,cycle_fields,t_us,cycle_idx,reflective_raw_red_corr,reflective_raw_ir_corr,transmission_raw_red_corr,transmission_raw_ir_corr,reflective_filtered_red_corr,reflective_filtered_ir_corr,transmission_filtered_red_corr,transmission_filtered_ir_corr`
- `META,pulseox_analog_map,reflective_raw=A0,transmission_raw=A1,reflective_filtered=A2,transmission_filtered=A3`
- `META,pulseox_led_pins,IR_D5,RED_D6`
- `META,pulseox_phase_sequence,RED_ON,DARK1,IR_ON,DARK2`

### `DATA`

Use `DATA` for continuous waveform samples in `CONT_HIGH` and `CONT_MED`.

Format:

`DATA,timestamp,sample1,sample2,...`

Examples:

- `DATA,1523456,512,487,530,501` for `CONT_HIGH`
- `DATA,1523,512,487,530,501` for `CONT_MED`

The meaning of `sample1,sample2,...` is declared at startup by `META,fields,...`.

### `PHASE`

Use `PHASE` for raw phase measurements in `PHASED_CYCLE`.

Format:

`PHASE,t_us,cycle_idx,phase,value1,value2,...`

PulseOx example:

`PHASE,125000,312,RED_ON,1842,1760,1901,1888`

For PulseOx, every `PHASE` packet always contains the same four physical analog channels:

- `reflective_raw`
- `transmission_raw`
- `reflective_filtered`
- `transmission_filtered`

Important rule:

- red versus IR comes from the `phase` field
- red versus IR does not come from different ADC pins

### `CYCLE`

Use `CYCLE` for reconstructed cycle values in `PHASED_CYCLE`.

Format:

`CYCLE,t_us,cycle_idx,value1,value2,...`

PulseOx example:

`CYCLE,127550,312,82,61,74,53,45,38,41,29`

For PulseOx, the corrected outputs are:

- `reflective_raw_red_corr`
- `reflective_raw_ir_corr`
- `transmission_raw_red_corr`
- `transmission_raw_ir_corr`
- `reflective_filtered_red_corr`
- `reflective_filtered_ir_corr`
- `transmission_filtered_red_corr`
- `transmission_filtered_ir_corr`

### `STAT`

Use `STAT` for low-rate status values or summaries.

Format:

`STAT,timestamp,key,value1,value2,...`

Examples:

- `STAT,5000,buffer_fill,12`
- `STAT,12000,heart_rate_bpm,72`

For `CONT_HIGH`, prefer microsecond timestamps when the status is tied to sample timing.

### `ERR`

Use `ERR` for device-side errors that should be visible in logs.

Format:

`ERR,timestamp,code,message`

Example:

`ERR,6400,SENSOR_TIMEOUT,No pulse detected`

For `CONT_HIGH`, prefer microsecond timestamps when the error is tied to sample timing.

---

## Continuous Lab Behavior

Current continuous workflows:

- ECG, EMG, and Blood Pressure use `DATA`
- `CONT_HIGH` emits `META,fields,t_us,...` and `DATA,t_us,...`
- `CONT_MED` emits `META,fields,t_ms,...` and `DATA,t_ms,...`
- UNO R4 WiFi firmware in this repo sets `analogReadResolution(14)` and emits `META,adc_resolution_bits,14`

---

## PulseOx Behavior

If a session uses the PulseOx preset, it switches to `PHASED_CYCLE`.

Current PulseOx rules:

- use fixed UNO R4 WiFi wiring
  - `A0 = reflective_raw`
  - `A1 = transmission_raw`
  - `A2 = reflective_filtered`
  - `A3 = transmission_filtered`
- drive the LED phases:
  - `RED_ON`
  - `DARK1`
  - `IR_ON`
  - `DARK2`
- emit one `PHASE` packet per phase
- sample all four channels during every phase
- emit one corrected `CYCLE` packet after `DARK2`

Current correction rule:

- `reflective_raw_red_corr = reflective_raw at RED_ON - reflective_raw at DARK1`
- `reflective_raw_ir_corr = reflective_raw at IR_ON - reflective_raw at DARK2`
- `transmission_raw_red_corr = transmission_raw at RED_ON - transmission_raw at DARK1`
- `transmission_raw_ir_corr = transmission_raw at IR_ON - transmission_raw at DARK2`
- `reflective_filtered_red_corr = reflective_filtered at RED_ON - reflective_filtered at DARK1`
- `reflective_filtered_ir_corr = reflective_filtered at IR_ON - reflective_filtered at DARK2`
- `transmission_filtered_red_corr = transmission_filtered at RED_ON - transmission_filtered at DARK1`
- `transmission_filtered_ir_corr = transmission_filtered at IR_ON - transmission_filtered at DARK2`

---

## Parser Expectations

Current parser behavior should:

- reject malformed lines
- reject unknown packet prefixes
- preserve the raw line on parse error
- save both host timestamp and device timestamp when available
- use `META,fields,...` for `DATA` columns
- use `META,phase_fields,...` for `PHASE` columns
- use `META,cycle_fields,...` for `CYCLE` columns

---

## Migration Note

- `CONT_HIGH` `DATA` packets now use `t_us` instead of `t_ms`
- `CONT_MED` timing is unchanged and still uses `t_ms`
- if you have older high-rate parsers, update them to accept `META,fields,t_us,...` and log device timestamps at microsecond resolution

---

## See Also

- [README.md](../README.md)
- [sampling_strategy.md](./sampling_strategy.md)
- [generated_firmware_workflow.md](./generated_firmware_workflow.md)
- [examples/session_csv/README.md](../examples/session_csv/README.md)
