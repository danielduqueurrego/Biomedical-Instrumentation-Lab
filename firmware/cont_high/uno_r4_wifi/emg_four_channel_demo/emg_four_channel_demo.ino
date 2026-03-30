// EMG four-channel reference sketch for the Arduino UNO R4 WiFi.
//
// Default manifest-aligned sampling behavior:
//   acquisition class: CONT_HIGH
//   sample rate: 2000 samples/s
//   timestamp field: t_us
//
// Default channel mapping:
//   A0 -> Raw EMG
//   A1 -> Rectified EMG
//   A2 -> Enveloped EMG
//   A3 -> Pressure
//
// Shared protocol packets:
//   META,lab,EMG_REFERENCE
//   META,firmware_version,1
//   META,acq_class,CONT_HIGH
//   META,rate_hz,2000
//   META,adc_resolution_bits,14
//   META,fields,t_us,A0,A1,A2,A3
//   DATA,t_us,A0,A1,A2,A3

const unsigned long BAUD_RATE = 230400;
const unsigned long SAMPLE_RATE_HZ = 2000;
const unsigned long SAMPLE_PERIOD_US = 500;

const int ANALOG_INPUT_PINS[] = {A0, A1, A2, A3};
const int ANALOG_INPUT_COUNT = sizeof(ANALOG_INPUT_PINS) / sizeof(ANALOG_INPUT_PINS[0]);

unsigned long nextSampleTimeUs = 0;

void writeMetadata() {
  Serial.println("META,lab,EMG_REFERENCE");
  Serial.println("META,firmware_version,1");
  Serial.println("META,acq_class,CONT_HIGH");
  Serial.println("META,rate_hz,2000");
  Serial.println("META,adc_resolution_bits,14");
  Serial.println("META,fields,t_us,A0,A1,A2,A3");
  Serial.println("META,selected_ports,A0,A1,A2,A3");
}

void setup() {
  Serial.begin(BAUD_RATE);

  while (!Serial && millis() < 3000) {
  }

  analogReadResolution(14);
  writeMetadata();
  nextSampleTimeUs = micros();
}

void loop() {
  const unsigned long nowUs = micros();
  if ((long)(nowUs - nextSampleTimeUs) < 0) {
    return;
  }

  nextSampleTimeUs += SAMPLE_PERIOD_US;

  Serial.print("DATA,");
  Serial.print(nowUs);

  for (int index = 0; index < ANALOG_INPUT_COUNT; ++index) {
    Serial.print(",");
    Serial.print(analogRead(ANALOG_INPUT_PINS[index]));
  }

  Serial.println();
}
