# Serial protocol v2

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
- `META,acq_class,CONT_MED`
- `META,rate_hz,200`
- `META,fields,t_ms,A0,A1,A2,A3`
- `META,selected_ports,A0,A1,A2,A3`
- `META,acq_class,PHASED_CYCLE`
- `META,cycle_rate_hz,100`
- `META,phase_rate_hz,400`
- `META,phase_fields,t_us,cycle_idx,phase,A0,A1,A2,A3,A4,A5`
- `META,cycle_fields,t_us,cycle_idx,Raw Red Reflective PD Output,Raw IR Reflective,...`
- `META,pulseox_signal_roles,RED,IR,RED,IR,RED,RED`
- `META,pulseox_led_pins,IR_D5,RED_D6`
- `META,pulseox_phase_sequence,RED_ON,DARK1,IR_ON,DARK2`

### `DATA`
Use for continuous waveform samples in `CONT_HIGH` and `CONT_MED`.

Format:
`DATA,t_ms,sample1,sample2,...`

Example:
`DATA,1523,512,487,530,501`

The meaning of `sample1,sample2,...` is declared by a `META,fields,...` packet at startup.

### `PHASE`
Use for raw phase measurements in `PHASED_CYCLE`.

Format:
`PHASE,t_us,cycle_idx,phase,value1,value2,...`

Example:
`PHASE,125000,312,RED_ON,1842,1760,1901`

The meaning of `value1,value2,...` is declared by `META,phase_fields,...`.

### `CYCLE`
Use for reconstructed cycle values in `PHASED_CYCLE`.

Format:
`CYCLE,t_us,cycle_idx,value1,value2,...`

Example:
`CYCLE,127550,312,1721,1645,1688`

The meaning of `value1,value2,...` is declared by `META,cycle_fields,...`.

### `STAT`
Use for low-rate status or summary values from the device.

Format:
`STAT,t_ms,key,value1,value2,...`

Examples:
- `STAT,5000,buffer_fill,12`
- `STAT,12000,heart_rate_bpm,72`

### `ERR`
Use for device-side errors that should be visible in logs.

Format:
`ERR,t_ms,code,message`

Example:
`ERR,6400,SENSOR_TIMEOUT,No pulse detected`

## GUI-generated firmware behavior

### Continuous labs
- ECG, EMG, and Blood Pressure use `DATA` packets.
- The generated sketch emits `META,fields,...` and then one `DATA` packet per sample.

### PulseOx labs
- If any active signal uses the `PulseOx` preset, the session runs in `PHASED_CYCLE` mode.
- All active signals must then be `PulseOx` signals.
- The generated sketch emits one `PHASE` packet for each phase:
  - `RED_ON`
  - `DARK1`
  - `IR_ON`
  - `DARK2`
- After `DARK2`, it emits one corrected `CYCLE` packet in configured signal order.

## Parser behavior
- Reject malformed lines
- Reject unknown packet prefixes
- Log the raw line on parse error
- Save both host timestamp and device timestamp when available
- For `DATA`, use `META,fields,...` to define the sample columns
- For `PHASE`, use `META,phase_fields,...` to define the raw phase columns
- For `CYCLE`, use `META,cycle_fields,...` to define the corrected cycle columns
