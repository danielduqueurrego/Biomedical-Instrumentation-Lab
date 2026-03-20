# Serial protocol v1

## General
- Transport: USB serial
- Default baud: 230400
- All packets are newline-terminated CSV strings
- No debug text during acquisition

## Continuous stream packet
Prefix: CONT

Format:
CONT,t_ms,ch1,ch2,ch3

Example:
CONT,1523,512,487,530

## Pulse-ox raw phase packet
Prefix: PX_RAW

Format:
PX_RAW,t_us,cycle_idx,phase,adc

Example:
PX_RAW,125000,312,RED_ON,1842
PX_RAW,125850,312,DARK1,121
PX_RAW,126700,312,IR_ON,1763
PX_RAW,127550,312,DARK2,118

## Pulse-ox reconstructed cycle packet
Prefix: PX_CYCLE

Format:
PX_CYCLE,t_us,cycle_idx,red_on,dark1,ir_on,dark2,red_corr,ir_corr

Example:
PX_CYCLE,127550,312,1842,121,1763,118,1721,1645

## Parser behavior
- Reject malformed lines
- Log raw line on parse error
- Save host timestamp and device timestamp
