# `PHASED_CYCLE` firmware

Place multi-phase cycle acquisition sketches here.

Typical labs:
- PulseOx

Expected packet mix:
- `META`
- `PHASE`
- `CYCLE`
- optional `STAT`
- optional `ERR`

Committed PulseOx reference sketch:
- `firmware/phased_cycle/uno_r4_wifi/pulse_ox_reference`

Current GUI-generated PulseOx behavior:
- drive `D6` for RED LED control
- drive `D5` for IR LED control
- step through `RED_ON`, `DARK1`, `IR_ON`, `DARK2`
- sample the same four wired optical channels during every phase:
  - `A0 = reflective_raw`
  - `A1 = transmission_raw`
  - `A2 = reflective_filtered`
  - `A3 = transmission_filtered`
- log one raw `PHASE` packet per phase with all four channel readings
- log one corrected `CYCLE` packet after `DARK2` with explicit RED-corrected and IR-corrected outputs
