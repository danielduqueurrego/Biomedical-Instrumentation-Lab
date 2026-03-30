// CONT_MED ECG reference sketch for Arduino UNO R4 WiFi.
//
// Default manifest-aligned sampling behavior:
//   acquisition class: CONT_MED
//   sample rate: 500 samples/s
//   timestamp field: t_ms
//
// Default channel mapping:
//   A0 -> Raw ECG
//   A1 -> Amplified ECG
//   A2 -> Comparator Output
//
// Shared protocol packets:
//   META,lab,ECG_REFERENCE
//   META,firmware_version,1
//   META,acq_class,CONT_MED
//   META,rate_hz,500
//   META,adc_resolution_bits,14
//   META,fields,t_ms,ECG_A0,ECG_A1,ECG_A2
//   DATA,t_ms,ECG_A0,ECG_A1,ECG_A2
//
// Why this sketch exists:
//   - ECG demonstrations benefit from a fixed named reference instead of the
//     generic three-channel analog demo.
//   - This sketch is labeled ECG_REFERENCE so students and TAs can confirm
//     the right firmware is running before recording data.
//   - The packet format matches docs/serial_protocol.md so the Python tools can
//     log and plot these values without custom parser changes.
//
// Student note:
//   Connect your ECG circuit outputs to A0, A1, and A2.
//   A0 receives the raw ECG signal before amplification.
//   A1 receives the amplified ECG signal.
//   A2 receives the comparator output used for R-peak detection.
//   If fewer channels are wired, leave unused pins as-is; ignore those columns.

const unsigned long BAUD_RATE = 230400;
const unsigned long SAMPLE_RATE_HZ = 500;
const unsigned long SAMPLE_PERIOD_US = 1000000UL / SAMPLE_RATE_HZ;  // 2000 us per sample.

const int ECG_CHANNEL_PINS[] = {A0, A1, A2};
const int ECG_CHANNEL_COUNT = sizeof(ECG_CHANNEL_PINS) / sizeof(ECG_CHANNEL_PINS[0]);

unsigned long nextSampleTimeUs = 0;

void writeMetadata() {
  Serial.println("META,lab,ECG_REFERENCE");
  Serial.println("META,firmware_version,1");
  Serial.println("META,acq_class,CONT_MED");
  Serial.println("META,rate_hz,500");
  Serial.println("META,adc_resolution_bits,14");
  Serial.println("META,fields,t_ms,ECG_A0,ECG_A1,ECG_A2");
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

  for (int index = 0; index < ECG_CHANNEL_COUNT; ++index) {
    Serial.print(",");
    Serial.print(analogRead(ECG_CHANNEL_PINS[index]));
  }

  Serial.println();
}
