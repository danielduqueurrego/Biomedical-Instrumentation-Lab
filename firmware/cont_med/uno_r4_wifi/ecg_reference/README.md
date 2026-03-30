# ECG Reference Sketch

Known-good ECG firmware for Arduino UNO R4 WiFi.

## Reference values
- acquisition class: `CONT_MED`
- sample rate: `500 samples/s`
- timestamp: `t_ms`
- channels: `ECG_A0`, `ECG_A1`, `ECG_A2`
- ADC: `analogReadResolution(14)`

## Pin map
- `A0` Raw ECG
- `A1` Amplified ECG
- `A2` Comparator output

## Packet fields
- `META,lab,ECG_REFERENCE`
- `META,acq_class,CONT_MED`
- `META,rate_hz,500`
- `META,fields,t_ms,ECG_A0,ECG_A1,ECG_A2`
- `DATA,t_ms,ECG_A0,ECG_A1,ECG_A2`
