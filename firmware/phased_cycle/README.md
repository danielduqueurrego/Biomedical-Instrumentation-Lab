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

Current GUI-generated PulseOx behavior:
- drive `D6` for RED LED control
- drive `D5` for IR LED control
- step through `RED_ON`, `DARK1`, `IR_ON`, `DARK2`
- log one raw `PHASE` packet per phase
- log one corrected `CYCLE` packet after `DARK2`
