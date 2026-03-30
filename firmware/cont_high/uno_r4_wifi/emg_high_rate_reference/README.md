# EMG High-Rate Reference

Minimal known-good EMG sketch for quick checks.

## Reference values
- acquisition class: `CONT_HIGH`
- sample rate: `1000 samples/s`
- timestamp: `t_us`
- channels: `EMG_A0`, `EMG_A1`
- ADC: `analogReadResolution(14)`

## Output packets
- `META,acq_class,CONT_HIGH`
- `META,rate_hz,1000`
- `META,adc_resolution_bits,14`
- `DATA,t_us,EMG_A0,EMG_A1`

## See also
- [CONT_HIGH overview](../../README.md)
- [EMG guide](../../../../docs/labs/emg.md)
