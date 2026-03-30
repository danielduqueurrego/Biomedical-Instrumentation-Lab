# PHASED_CYCLE Firmware

Multi-phase firmware used for pulse oximetry-style acquisition.

## Included sketch
- `uno_r4_wifi/pulse_ox_reference`

## Expected protocol behavior
- acquisition class: `PHASED_CYCLE`
- packet types: `META`, `PHASE`, `CYCLE`
- phase order: `RED_ON`, `DARK1`, `IR_ON`, `DARK2`

## PulseOx model summary
- `D6` controls RED LED
- `D5` controls IR LED
- analog channels are sampled each phase and corrected cycle values are emitted

## Related docs
- [Pulse Ox guide](../../docs/labs/pulse_ox.md)
- [Serial protocol](../../docs/serial_protocol.md)
