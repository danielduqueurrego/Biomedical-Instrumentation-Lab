// CONT_MED three-channel data demo for Arduino UNO R4 WiFi.
//
// Shared protocol packets:
//   META,lab,CONT_MED_THREE_CHANNEL
//   META,acq_class,CONT_MED
//   META,rate_hz,120
//   META,fields,t_ms,ch1,ch2,ch3
//   DATA,t_ms,ch1,ch2,ch3
//
// This sketch reads three analog inputs and sends one DATA CSV line at about
// 120 Hz. The channel pin assignments are grouped here so they are easy to
// change if your lab hardware uses different analog inputs.

const unsigned long BAUD_RATE = 230400;
const unsigned long SAMPLE_PERIOD_US = 8333;  // About 120 Hz.

const int CHANNEL_1_PIN = A0;
const int CHANNEL_2_PIN = A1;
const int CHANNEL_3_PIN = A2;

unsigned long nextSampleTimeUs = 0;

void writeMetadata() {
  Serial.println("META,lab,CONT_MED_THREE_CHANNEL");
  Serial.println("META,acq_class,CONT_MED");
  Serial.println("META,rate_hz,120");
  Serial.println("META,fields,t_ms,ch1,ch2,ch3");
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

  const int ch1 = analogRead(CHANNEL_1_PIN);
  const int ch2 = analogRead(CHANNEL_2_PIN);
  const int ch3 = analogRead(CHANNEL_3_PIN);
  const unsigned long tMs = millis();

  Serial.print("DATA,");
  Serial.print(tMs);
  Serial.print(",");
  Serial.print(ch1);
  Serial.print(",");
  Serial.print(ch2);
  Serial.print(",");
  Serial.println(ch3);
}
