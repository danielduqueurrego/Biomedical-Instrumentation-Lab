# Blood Pressure Reference Sketch

> Named `CONT_MED` reference sketch for Blood Pressure acquisition on the Arduino UNO R4 WiFi.

Use this sketch when you want a known-good blood pressure acquisition sketch that clearly identifies itself as `BLOOD_PRESSURE_REFERENCE` in the startup metadata.

---

## Quick Reference

| Item | Current value |
| --- | --- |
| Acquisition class | `CONT_MED` |
| Sample rate | `200 samples/s` |
| Timestamp field | `t_ms` |
| Channels | `BP_A0` |
| ADC setting | `analogReadResolution(14)` |
| Firmware version | `1` |

---

## Pin Mapping

- `A0 = Pressure Waveform` — analog output from the pressure transducer or cuff sensor

---

## Packet Layout

Startup metadata:

- `META,lab,BLOOD_PRESSURE_REFERENCE`
- `META,firmware_version,1`
- `META,acq_class,CONT_MED`
- `META,rate_hz,200`
- `META,adc_resolution_bits,14`
- `META,fields,t_ms,BP_A0`

Data rows:

- `DATA,t_ms,BP_A0`

---

## See Also

- [CONT_MED firmware overview](../../README.md)
- [Blood Pressure lab guide](../../../../docs/labs/blood_pressure.md)
- [Sampling strategy](../../../../docs/sampling_strategy.md)
- [Serial protocol](../../../../docs/serial_protocol.md)
