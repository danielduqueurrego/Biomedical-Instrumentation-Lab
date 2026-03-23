# Sampling strategy

These presets are software starting points for student labs. They are not hardware guarantees and should be validated on each lab board.

## Acquisition class guidance

### `CONT_HIGH`
- Target use: fast waveform capture
- Typical range: 1000 to 4000 samples per second
- Logging rule: save every sample to CSV
- Timing rule: use `t_us` so the device timestamp still resolves individual samples
- Plotting rule: update the plot less often than samples arrive

### `CONT_MED`
- Target use: medium-rate waveform capture
- Typical range: 100 to 1000 samples per second
- Logging rule: save every sample to CSV
- Plotting rule: redraw about 5 to 10 times per second

### `PHASED_CYCLE`
- Target use: repeated multi-phase measurement cycles
- Typical range: 25 to 150 cycles per second
- Logging rule: keep both raw `PHASE` packets and reconstructed `CYCLE` packets
- Plotting rule: emphasize corrected cycle values instead of every raw phase

## Default presets

| Lab | Acquisition class | Default rate | Primary packets | Default fields | Plot default |
| --- | --- | --- | --- | --- | --- |
| EMG | `CONT_HIGH` | 2000 samples/s | `META`, `DATA`, `STAT`, `ERR` | `t_us`, `ch1` | 5 s window, 50 ms redraw |
| ECG | `CONT_MED` | 500 samples/s | `META`, `DATA`, `STAT`, `ERR` | `t_ms`, `ch1` | 10 s window, 100 ms redraw |
| PulseOx | `PHASED_CYCLE` | 100 cycles/s | `META`, `PHASE`, `CYCLE`, `STAT`, `ERR` | `t_us`, `cycle_idx`, corrected values | 15 s window, 100 ms redraw |
| Blood Pressure | `CONT_MED` | 200 samples/s | `META`, `DATA`, `STAT`, `ERR` | `t_ms`, `pressure` | 20 s window, 200 ms redraw |

## Blood pressure note

Blood pressure is treated as a continuous waveform lab.

- Students manually control cuff inflation and deflation.
- The software logs the waveform continuously with `DATA`.
- The project does not emit procedure-stage packets for blood pressure.

## PulseOx note

PulseOx uses four optical phases per cycle:
- `RED_ON`
- `DARK1`
- `IR_ON`
- `DARK2`

The GUI-generated firmware logs every phase sample with `PHASE`, sampling the same four physical channels on each phase:
- `A0 = reflective_raw`
- `A1 = transmission_raw`
- `A2 = reflective_filtered`
- `A3 = transmission_filtered`

It then reconstructs corrected cycle values with `CYCLE`, where RED vs IR is inferred from the phase timing instead of separate ADC pins.

## Migration note

- `CONT_HIGH` data fields now begin with `t_us`.
- `CONT_MED` remains on `t_ms`.
