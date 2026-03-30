# EMG Four-Channel Demo

Fixed four-channel EMG demo aligned with repository defaults.

## Reference values
- acquisition class: `CONT_HIGH`
- sample rate: `2000 samples/s`
- timestamp: `t_us`
- ADC: `analogReadResolution(14)`

## Pin map
- `A0` Raw EMG
- `A1` Rectified EMG
- `A2` Envelope EMG
- `A3` Pressure/aux input

## Output packets
- `META,lab,EMG_REFERENCE`
- `META,acq_class,CONT_HIGH`
- `META,rate_hz,2000`
- `META,fields,t_us,A0,A1,A2,A3`
- `DATA,t_us,A0,A1,A2,A3`

## See also
- [EMG guide](../../../../docs/labs/emg.md)
- [Serial protocol](../../../../docs/serial_protocol.md)
