# CONT_MED Analog Demo

Simple continuous demo sketch for classroom checks and smoke tests.

## Reference values
- acquisition class: `CONT_MED`
- approximate rate: `120 samples/s`
- timestamp: `t_ms`
- analog inputs: `A0` to `A5`
- ADC: `analogReadResolution(14)`

## Typical use
Use this for quick board/serial validation before running a specific lab preset.

## Commands
- compile: `python tools/arduino_cli.py compile-demo`
- upload: `./tools/upload_cont_med_three_channel.sh`
