# Serial protocol v4

## General
- Transport: USB serial
- Default baud: 230400
- All packets are newline-terminated ASCII CSV strings
- Field 0 is always the packet prefix
- No debug text during acquisition
- Python loggers add host timestamps on receipt
- Device packets should include a device timestamp in the first payload field whenever timing matters

## Shared packet types

### `META`
Use for startup metadata and packet layout declarations.

Format:
`META,key,value1,value2,...`

Examples:
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
Use for continuous waveform samples in `CONT_HIGH` and `CONT_MED`.

Format:
`DATA,timestamp,sample1,sample2,...`

`CONT_HIGH` example:
`DATA,1523456,512,487,530,501`

`CONT_MED` example:
`DATA,1523,512,487,530,501`

The meaning of `sample1,sample2,...` is declared by a `META,fields,...` packet at startup.

Timing rule:
- `CONT_HIGH` uses `t_us`
- `CONT_MED` uses `t_ms`

### `PHASE`
Use for raw phase measurements in `PHASED_CYCLE`.

Format:
`PHASE,t_us,cycle_idx,phase,value1,value2,...`

PulseOx example:
`PHASE,125000,312,RED_ON,1842,1760,1901,1888`

For PulseOx, the `PHASE` payload always contains the same four physical analog channels:
- `reflective_raw`
- `transmission_raw`
- `reflective_filtered`
- `transmission_filtered`

Red vs IR is inferred from the `phase` field, not from separate ADC pins.

### `CYCLE`
Use for reconstructed cycle values in `PHASED_CYCLE`.

Format:
`CYCLE,t_us,cycle_idx,value1,value2,...`

PulseOx example:
`CYCLE,127550,312,82,61,74,53,45,38,41,29`

For PulseOx, the `CYCLE` payload contains these corrected outputs:
- `reflective_raw_red_corr`
- `reflective_raw_ir_corr`
- `transmission_raw_red_corr`
- `transmission_raw_ir_corr`
- `reflective_filtered_red_corr`
- `reflective_filtered_ir_corr`
- `transmission_filtered_red_corr`
- `transmission_filtered_ir_corr`

### `STAT`
Use for low-rate status or summary values from the device.

Format:
`STAT,timestamp,key,value1,value2,...`

Examples:
- `STAT,5000,buffer_fill,12`
- `STAT,12000,heart_rate_bpm,72`

For `CONT_HIGH`, prefer microsecond timestamps when the status value is tied to sample timing.

### `ERR`
Use for device-side errors that should be visible in logs.

Format:
`ERR,timestamp,code,message`

Example:
`ERR,6400,SENSOR_TIMEOUT,No pulse detected`

For `CONT_HIGH`, prefer microsecond timestamps when the error is tied to sample timing.

## GUI-generated firmware behavior

### Continuous labs
- ECG, EMG, and Blood Pressure use `DATA` packets.
- `CONT_HIGH` continuous labs emit `META,fields,t_us,...` and `DATA,t_us,...`.
- `CONT_MED` continuous labs emit `META,fields,t_ms,...` and `DATA,t_ms,...`.
- Current UNO R4 WiFi firmware paths also emit `META,adc_resolution_bits,14` and call `analogReadResolution(14)` in `setup()`.

### PulseOx labs
- If any active signal uses the `PulseOx` preset, the session runs in `PHASED_CYCLE` mode.
- All active signals must then be `PulseOx` signals.
- PulseOx uses fixed UNO R4 WiFi wiring:
  - `A0 = reflective_raw`
  - `A1 = transmission_raw`
  - `A2 = reflective_filtered`
  - `A3 = transmission_filtered`
- The generated sketch emits one `PHASE` packet for each phase:
  - `RED_ON`
  - `DARK1`
  - `IR_ON`
  - `DARK2`
- Every `PHASE` packet samples all four channels from `A0` to `A3`.
- After `DARK2`, the sketch emits one corrected `CYCLE` packet with eight explicit corrected outputs.

## PulseOx correction rule

The generated firmware uses a phase-paired dark subtraction:
- `reflective_raw_red_corr = reflective_raw at RED_ON - reflective_raw at DARK1`
- `reflective_raw_ir_corr = reflective_raw at IR_ON - reflective_raw at DARK2`
- `transmission_raw_red_corr = transmission_raw at RED_ON - transmission_raw at DARK1`
- `transmission_raw_ir_corr = transmission_raw at IR_ON - transmission_raw at DARK2`
- `reflective_filtered_red_corr = reflective_filtered at RED_ON - reflective_filtered at DARK1`
- `reflective_filtered_ir_corr = reflective_filtered at IR_ON - reflective_filtered at DARK2`
- `transmission_filtered_red_corr = transmission_filtered at RED_ON - transmission_filtered at DARK1`
- `transmission_filtered_ir_corr = transmission_filtered at IR_ON - transmission_filtered at DARK2`

## Migration note

- `CONT_HIGH` `DATA` packets now use `t_us` instead of `t_ms`.
- `CONT_MED` packet timing is unchanged and still uses `t_ms`.
- If you have older high-rate CSV parsers, update them to accept `META,fields,t_us,...` and log the Arduino timestamp at microsecond resolution.

## Parser behavior
- Reject malformed lines
- Reject unknown packet prefixes
- Log the raw line on parse error
- Save both host timestamp and device timestamp when available
- For `DATA`, use `META,fields,...` to define the sample columns
- For `PHASE`, use `META,phase_fields,...` to define the raw phase columns
- For `CYCLE`, use `META,cycle_fields,...` to define the corrected cycle columns
