// CONT_MED analog-bank demo for Arduino UNO R4 WiFi.
//
// Shared protocol packets:
//   META,lab,CONT_MED_ANALOG_BANK
//   META,acq_class,CONT_MED
//   META,rate_hz,120
//   META,fields,t_ms,A0,A1,A2,A3,A4,A5
//   DATA,t_ms,A0,A1,A2,A3,A4,A5
//
// This sketch reads the six standard UNO R4 WiFi analog inputs and sends one
// DATA CSV line at about 120 Hz. The Python GUI can label and select any subset
// of these six inputs without changing the firmware.
//
// Note:
// The student GUI compile/upload workflow generates a custom sketch with the
// selected analog ports and the highest selected preset rate. This file remains
// the fixed reference example in the repository.

const unsigned long BAUD_RATE = 230400;
const unsigned long SAMPLE_PERIOD_US = 8333;  // About 120 Hz.

const int ANALOG_INPUT_PINS[] = {A0, A1, A2, A3, A4, A5};
const int ANALOG_INPUT_COUNT = sizeof(ANALOG_INPUT_PINS) / sizeof(ANALOG_INPUT_PINS[0]);

unsigned long nextSampleTimeUs = 0;

void writeMetadata() {
  Serial.println("META,lab,CONT_MED_ANALOG_BANK");
  Serial.println("META,acq_class,CONT_MED");
  Serial.println("META,rate_hz,120");
  Serial.println("META,fields,t_ms,A0,A1,A2,A3,A4,A5");
}

void setup() {
  Serial.begin(BAUD_RATE);

  // Wait briefly for the USB serial connection so the first lines are not lost
  // when students open the Python app right after reset.
  while (!Serial && millis() < 3000) {
  }

  writeMetadata();
  nextSampleTimeUs = micros();
}

void loop() {
  const unsigned long nowUs = micros();

  if ((long)(nowUs - nextSampleTimeUs) < 0) {
    return;
  }

  nextSampleTimeUs += SAMPLE_PERIOD_US;

  const unsigned long tMs = millis();

  Serial.print("DATA,");
  Serial.print(tMs);

  for (int index = 0; index < ANALOG_INPUT_COUNT; ++index) {
    Serial.print(",");
    Serial.print(analogRead(ANALOG_INPUT_PINS[index]));
  }

  Serial.println();
}
