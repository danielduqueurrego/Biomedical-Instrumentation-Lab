# ECG Reference Sketch

> Named `CONT_MED` reference sketch for ECG acquisition on the Arduino UNO R4 WiFi.

Use this sketch when you want a known-good ECG acquisition sketch that clearly identifies itself as `ECG_REFERENCE` in the startup metadata.

---

## 📌 Quick Reference

| Item | Current value |
| --- | --- |
| Acquisition class | `CONT_MED` |
| Sample rate | `500 samples/s` |
| Timestamp field | `t_ms` |
| Channels | `ECG_A0`, `ECG_A1`, `ECG_A2` |
| ADC setting | `analogReadResolution(14)` |
| Firmware version | `1` |

---

## 🔌 Pin Mapping

- `A0 = Raw ECG` — signal before amplification
- `A1 = Amplified ECG` — signal after instrumentation amplifier
- `A2 = Comparator Output` — digital comparator used for R-peak detection

---

## 📡 Packet Layout

Startup metadata:

- `META,lab,ECG_REFERENCE`
- `META,firmware_version,1`
- `META,acq_class,CONT_MED`
- `META,rate_hz,500`
- `META,adc_resolution_bits,14`
- `META,fields,t_ms,ECG_A0,ECG_A1,ECG_A2`

Data rows:

- `DATA,t_ms,ECG_A0,ECG_A1,ECG_A2`

---

## 🔗 See Also

- [CONT_MED firmware overview](../../README.md)
- [ECG lab guide](../../../../docs/labs/ecg.md)
- [Sampling strategy](../../../../docs/sampling_strategy.md)
- [Serial protocol](../../../../docs/serial_protocol.md)
