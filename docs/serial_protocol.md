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
- `META,lab,CONT_MED_THREE_CHANNEL`
- `META,acq_class,CONT_MED`
- `META,rate_hz,120`
- `META,fields,t_ms,ch1,ch2,ch3`

### `DATA`
Use for continuous waveform samples in `CONT_HIGH`, `CONT_MED`, and `PROC_CONT`.

Format:
`DATA,t_ms,sample1,sample2,...`

Example:
`DATA,1523,512,487,530`

The meaning of `sample1,sample2,...` is declared by a `META,fields,...` packet at startup.

### `PHASE`
Use for raw phase measurements in `PHASED_CYCLE`.

Format:
`PHASE,t_us,cycle_idx,phase,value1,value2,...`

Example:
`PHASE,125000,312,RED_ON,1842`

### `CYCLE`
Use for reconstructed cycle values in `PHASED_CYCLE`.

Format:
`CYCLE,t_us,cycle_idx,value1,value2,...`

Example:
`CYCLE,127550,312,1721,1645`

### `EVENT`
Use for stage changes, procedure markers, or notable acquisition events.

Format:
`EVENT,t_ms,event_name,value1,value2,...`

Examples:
- `EVENT,5200,stage,INFLATE,enter`
- `EVENT,18340,button,MARK`

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

## Parser behavior
- Reject malformed lines
- Reject unknown packet prefixes
- Log the raw line on parse error
- Save both host timestamp and device timestamp when available
- For `DATA`, use `META,fields,...` to define the sample columns
- For blood pressure, keep procedure stages in `EVENT` packets instead of overloading `DATA`
