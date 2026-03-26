# Sampling Strategy

> Default sampling guidance for the current labs and acquisition classes.

Use this document when you need the current default rates, timing fields, and plotting expectations. These values are software defaults, not hardware guarantees, so bench validation still matters.

---

## Start Here

The repo uses a small set of default presets so the GUI, generated firmware, reference sketches, and protocol docs stay aligned.

Current shared assumptions:

- the UNO R4 WiFi ADC is configured to `14-bit` with `analogReadResolution(14)`
- startup metadata includes `META,adc_resolution_bits,14`
- continuous labs log every sample
- PulseOx logs both raw `PHASE` rows and corrected `CYCLE` rows

---

## Acquisition Class Guidance

### `CONT_HIGH`

Use for fast waveform capture.

Current guidance:

- typical range: `1000` to `4000 samples/s`
- log every sample
- use `t_us`
- update the plot less often than samples arrive

### `CONT_MED`

Use for medium-rate waveform capture.

Current guidance:

- typical range: `100` to `1000 samples/s`
- log every sample
- use `t_ms`
- redraw the plot at a comfortable classroom rate

### `PHASED_CYCLE`

Use for repeated multi-phase measurement cycles.

Current guidance:

- typical range: `25` to `150 cycles/s`
- keep both `PHASE` and `CYCLE` rows
- use `t_us`
- emphasize corrected cycle values in the live plot

---

## Current Default Presets

| Lab | Acquisition class | Default rate | Primary packets | Default timing field | Plot default |
| --- | --- | --- | --- | --- | --- |
| EMG | `CONT_HIGH` | `2000 samples/s` | `META`, `DATA`, `STAT`, `ERR` | `t_us` | 5 s window, 50 ms redraw |
| ECG | `CONT_MED` | `500 samples/s` | `META`, `DATA`, `STAT`, `ERR` | `t_ms` | 10 s window, 100 ms redraw |
| PulseOx | `PHASED_CYCLE` | `100 cycles/s` | `META`, `PHASE`, `CYCLE`, `STAT`, `ERR` | `t_us` | 15 s window, 100 ms redraw |
| Blood Pressure | `CONT_MED` | `200 samples/s` | `META`, `DATA`, `STAT`, `ERR` | `t_ms` | 20 s window, 200 ms redraw |

---

## Lab Notes

### EMG

- high-rate continuous waveform lab
- current default is `2000 samples/s`
- use `t_us`

### ECG

- medium-rate continuous waveform lab
- current default is `500 samples/s`
- use `t_ms`

### PulseOx

- phased-cycle optical lab
- current default is `100 cycles/s`
- four phases per cycle, so the raw phase rate is `400 phase samples/s`

### Blood Pressure

- continuous waveform lab
- current default is `200 samples/s`
- no procedure-stage packets are emitted

---

## Validation Reminder

These defaults are starting points. Bench testing should still record:

- target rate
- achieved rate
- malformed packet count
- packet loss notes
- plot responsiveness
- hardware notes

Use the validation docs after any board, firmware, or lab-profile change.

---

## See Also

- [README.md](../README.md)
- [acquisition_architecture.md](./acquisition_architecture.md)
- [serial_protocol.md](./serial_protocol.md)
- [validation/README.md](./validation/README.md)
