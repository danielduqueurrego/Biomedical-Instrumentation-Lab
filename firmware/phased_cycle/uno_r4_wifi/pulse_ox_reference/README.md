# Pulse Ox Reference Sketch

Known-good phased-cycle pulse oximetry sketch for Arduino UNO R4 WiFi.

## Reference values
- acquisition class: `PHASED_CYCLE`
- cycle rate: `100 cycles/s`
- phase rate: `400 phase samples/s`
- timestamp: `t_us`
- ADC: `analogReadResolution(14)`

## Pin map
- `A0` reflective_raw
- `A1` transmission_raw
- `A2` reflective_filtered
- `A3` transmission_filtered
- `D6` RED LED control
- `D5` IR LED control

## Packets
- startup `META`
- per-phase `PHASE`
- corrected-cycle `CYCLE`

## Notes
Red/IR separation is determined by phase timing, not separate analog pins.
