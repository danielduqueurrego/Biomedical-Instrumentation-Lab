# EMG Four-Channel Demo

> Known committed EMG reference sketch for the Arduino UNO R4 WiFi.

Use this sketch when you want a fixed `CONT_HIGH` EMG example that matches the repo manifest defaults.

---

## Quick Reference

| Item | Current value |
| --- | --- |
| Acquisition class | `CONT_HIGH` |
| Sample rate | `2000 samples/s` |
| Timestamp field | `t_us` |
| ADC setting | `analogReadResolution(14)` |

---

## Pin Mapping

- `A0 = Raw EMG`
- `A1 = Rectified EMG`
- `A2 = Enveloped EMG`
- `A3 = Pressure`

---

## Packet Layout

Startup metadata:

- `META,lab,EMG_REFERENCE`
- `META,acq_class,CONT_HIGH`
- `META,rate_hz,2000`
- `META,adc_resolution_bits,14`
- `META,fields,t_us,A0,A1,A2,A3`

Data rows:

- `DATA,t_us,A0,A1,A2,A3`

---

## See Also

- [EMG lab guide](../../../../docs/labs/emg.md)
- [Sampling strategy](../../../../docs/sampling_strategy.md)
- [Serial protocol](../../../../docs/serial_protocol.md)
