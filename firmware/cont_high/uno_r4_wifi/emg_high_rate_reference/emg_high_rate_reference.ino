// CONT_HIGH EMG reference sketch for Arduino UNO R4 WiFi.
//
// Shared protocol packets:
//   META,lab,CONT_HIGH_EMG_REFERENCE
//   META,acq_class,CONT_HIGH
//   META,rate_hz,1000
//   META,adc_resolution_bits,14
//   META,fields,t_us,EMG_A0,EMG_A1
//   DATA,t_us,EMG_A0,EMG_A1
//
// Why this sketch exists:
//   - EMG demonstrations benefit from higher sample rates than slow trend signals.
//   - This reference streams two analog channels at a 1 kHz target so students can
//     compare two muscle locations during the same acquisition.
//   - The packet format matches docs/serial_protocol.md so the Python tools can log
//     and plot these values without custom parser changes.
//
// Student note:
//   Connect your conditioned EMG outputs to A0 and/or A1.
//   If only one channel is connected, leave the other pin as-is and ignore that column.

const unsigned long BAUD_RATE = 230400;
const unsigned long SAMPLE_RATE_HZ = 1000;
const unsigned long SAMPLE_PERIOD_US = 1000000UL / SAMPLE_RATE_HZ;  // 1000 us per sample.

const int EMG_CHANNEL_PINS[] = {A0, A1};
const int EMG_CHANNEL_COUNT = sizeof(EMG_CHANNEL_PINS) / sizeof(EMG_CHANNEL_PINS[0]);

unsigned long nextSampleTimeUs = 0;

void writeMetadata() {
  Serial.println("META,lab,CONT_HIGH_EMG_REFERENCE");
  Serial.println("META,acq_class,CONT_HIGH");
  Serial.println("META,rate_hz,1000");
  Serial.println("META,adc_resolution_bits,14");
  Serial.println("META,fields,t_us,EMG_A0,EMG_A1");
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
  Serial.print(nowUs);

  for (int index = 0; index < EMG_CHANNEL_COUNT; ++index) {
    Serial.print(",");
    Serial.print(analogRead(EMG_CHANNEL_PINS[index]));
  }

  Serial.println();
}
