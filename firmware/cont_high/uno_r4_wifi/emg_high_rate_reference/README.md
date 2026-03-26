# EMG High-Rate Reference

> Simple fixed `CONT_HIGH` sketch for quick Arduino CLI compile and upload checks.

Use this sketch when you want the fastest known-good high-rate upload path without the full four-channel EMG demo.

---

## Quick Reference

| Item | Current value |
| --- | --- |
| Acquisition class | `CONT_HIGH` |
| Sample rate | `1000 samples/s` |
| Timestamp field | `t_us` |
| Channels | `EMG_A0`, `EMG_A1` |
| ADC setting | `analogReadResolution(14)` |

---

## Packet Layout

- `META,acq_class,CONT_HIGH`
- `META,rate_hz,1000`
- `META,adc_resolution_bits,14`
- `DATA,t_us,EMG_A0,EMG_A1`

---

## Quick Use

From the repository root:

- macOS/Linux: `./tools/upload_cont_high_emg_reference.sh`
- Windows: `tools\upload_cont_high_emg_reference.bat`

If auto-detect cannot find the board port:

- `python tools/arduino_cli.py upload-cont-high-emg --port /dev/ttyACM0`
- `python tools/arduino_cli.py upload-cont-high-emg --port COM3`

---

## See Also

- [CONT_HIGH firmware overview](../../README.md)
- [EMG lab guide](../../../../docs/labs/emg.md)
