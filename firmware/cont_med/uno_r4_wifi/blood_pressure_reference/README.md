# Blood Pressure Reference Sketch

Known-good blood pressure firmware for Arduino UNO R4 WiFi.

## Reference values
- acquisition class: `CONT_MED`
- sample rate: `200 samples/s`
- timestamp: `t_ms`
- channel: `BP_A0`
- ADC: `analogReadResolution(14)`

## Pin map
- `A0` Pressure waveform input

## Packet fields
- `META,lab,BLOOD_PRESSURE_REFERENCE`
- `META,acq_class,CONT_MED`
- `META,rate_hz,200`
- `META,fields,t_ms,BP_A0`
- `DATA,t_ms,BP_A0`
