// CONT_MED Blood Pressure reference sketch for Arduino UNO R4 WiFi.
//
// Default manifest-aligned sampling behavior:
//   acquisition class: CONT_MED
//   sample rate: 200 samples/s
//   timestamp field: t_ms
//
// Default channel mapping:
//   A0 -> Pressure Waveform
//
// Shared protocol packets:
//   META,lab,BLOOD_PRESSURE_REFERENCE
//   META,firmware_version,1
//   META,acq_class,CONT_MED
//   META,rate_hz,200
//   META,adc_resolution_bits,14
//   META,fields,t_ms,BP_A0
//   DATA,t_ms,BP_A0
//
// Why this sketch exists:
//   - Blood pressure demonstrations benefit from a fixed named reference instead
//     of the generic three-channel analog demo.
//   - This sketch is labeled BLOOD_PRESSURE_REFERENCE so students and TAs can
//     confirm the right firmware is running before recording data.
//   - The packet format matches docs/serial_protocol.md so the Python tools can
//     log and plot these values without custom parser changes.
//
// Student note:
//   Connect your pressure transducer or cuff-sensor output to A0.
//   200 samples/s is sufficient to capture blood pressure waveform features
//   including systolic and diastolic peaks.

const unsigned long BAUD_RATE = 230400;
const unsigned long SAMPLE_RATE_HZ = 200;
const unsigned long SAMPLE_PERIOD_US = 1000000UL / SAMPLE_RATE_HZ;  // 5000 us per sample.

const int BP_CHANNEL_PINS[] = {A0};
const int BP_CHANNEL_COUNT = sizeof(BP_CHANNEL_PINS) / sizeof(BP_CHANNEL_PINS[0]);

unsigned long nextSampleTimeUs = 0;

void writeMetadata() {
  Serial.println("META,lab,BLOOD_PRESSURE_REFERENCE");
  Serial.println("META,firmware_version,1");
  Serial.println("META,acq_class,CONT_MED");
  Serial.println("META,rate_hz,200");
  Serial.println("META,adc_resolution_bits,14");
  Serial.println("META,fields,t_ms,BP_A0");
}

void setup() {
  Serial.begin(BAUD_RATE);

  // Wait briefly so students do not miss startup metadata immediately after reset.
  while (!Serial && millis() < 3000) {
  }

  analogReadResolution(14);
  writeMetadata();
  nextSampleTimeUs = micros();
}

void loop() {
  const unsigned long nowUs = micros();

  // Keep loop timing stable by waiting until the next sample deadline.
  if ((long)(nowUs - nextSampleTimeUs) < 0) {
    return;
  }

  // Schedule the next sample first so timing drift stays small.
  nextSampleTimeUs += SAMPLE_PERIOD_US;

  Serial.print("DATA,");
  Serial.print(millis());  // CONT_MED uses millisecond timestamps.

  for (int index = 0; index < BP_CHANNEL_COUNT; ++index) {
    Serial.print(",");
    Serial.print(analogRead(BP_CHANNEL_PINS[index]));
  }

  Serial.println();
}
