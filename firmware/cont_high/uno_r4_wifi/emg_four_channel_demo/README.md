# EMG four-channel demo

This reference sketch targets the Arduino UNO R4 WiFi and the default EMG lab wiring.

Default sampling behavior:
- acquisition class: `CONT_HIGH`
- sample rate: `2000` samples/s
- timestamp field: `t_us`

Default channel mapping:
- `A0 = Raw EMG`
- `A1 = Rectified EMG`
- `A2 = Enveloped EMG`
- `A3 = Pressure`

Shared protocol packets:
- `META,lab,EMG_REFERENCE`
- `META,acq_class,CONT_HIGH`
- `META,rate_hz,2000`
- `META,fields,t_us,A0,A1,A2,A3`
- `DATA,t_us,A0,A1,A2,A3`

This sketch keeps the code simple for students and matches the shared Python manifest defaults.
