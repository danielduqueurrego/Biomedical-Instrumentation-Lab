// PulseOx reference sketch for the Arduino UNO R4 WiFi.
//
// Fixed hardware model:
//   A0 -> reflective raw photodiode output
//   A1 -> transmission raw photodiode output
//   A2 -> filtered reflective photodiode output
//   A3 -> filtered transmission photodiode output
//
// LED control:
//   D6 -> RED LED
//   D5 -> IR LED
//
// Phase order:
//   RED_ON -> DARK1 -> IR_ON -> DARK2
//
// Shared protocol packets:
//   META,lab,PULSEOX_REFERENCE
//   META,acq_class,PHASED_CYCLE
//   META,adc_resolution_bits,14
//   META,cycle_rate_hz,100
//   META,phase_rate_hz,400
//   META,phase_fields,t_us,cycle_idx,phase,reflective_raw,transmission_raw,reflective_filtered,transmission_filtered
//   PHASE,t_us,cycle_idx,phase,reflective_raw,transmission_raw,reflective_filtered,transmission_filtered
//   META,cycle_fields,t_us,cycle_idx,reflective_raw_red_corr,reflective_raw_ir_corr,transmission_raw_red_corr,transmission_raw_ir_corr,reflective_filtered_red_corr,reflective_filtered_ir_corr,transmission_filtered_red_corr,transmission_filtered_ir_corr
//   CYCLE,t_us,cycle_idx,reflective_raw_red_corr,reflective_raw_ir_corr,transmission_raw_red_corr,transmission_raw_ir_corr,reflective_filtered_red_corr,reflective_filtered_ir_corr,transmission_filtered_red_corr,transmission_filtered_ir_corr
//
// The first ADC result after switching channels can be contaminated by the
// previous channel. This reference sketch discards one read and averages two
// settled reads per channel to reduce spike-like artifacts in the corrected
// cycle output.

const unsigned long BAUD_RATE = 230400;
const unsigned long CYCLE_RATE_HZ = 100;
const unsigned long CYCLE_PERIOD_US = 1000000UL / CYCLE_RATE_HZ;
const unsigned long PHASE_PERIOD_US = CYCLE_PERIOD_US / 4;
const int ADC_RESOLUTION_BITS = 14;
const int ADC_SETTLED_SAMPLE_COUNT = 2;

const int IR_LED_PIN = 5;
const int RED_LED_PIN = 6;
const int PHASE_COUNT = 4;

const int ANALOG_INPUT_PINS[] = {A0, A1, A2, A3};
const int ANALOG_INPUT_COUNT = sizeof(ANALOG_INPUT_PINS) / sizeof(ANALOG_INPUT_PINS[0]);

enum PulseOxPhase {
  RED_ON = 0,
  DARK1 = 1,
  IR_ON = 2,
  DARK2 = 3,
};

enum PulseOxChannel {
  REFLECTIVE_RAW = 0,
  TRANSMISSION_RAW = 1,
  REFLECTIVE_FILTERED = 2,
  TRANSMISSION_FILTERED = 3,
};

PulseOxPhase currentPhase = RED_ON;
unsigned long nextPhaseCaptureUs = 0;
unsigned long currentCycleIndex = 0;
int phaseSamples[PHASE_COUNT][ANALOG_INPUT_COUNT];

void applyPulseOxPhase() {
  switch (currentPhase) {
    case RED_ON:
      digitalWrite(RED_LED_PIN, HIGH);
      digitalWrite(IR_LED_PIN, LOW);
      break;
    case DARK1:
      digitalWrite(RED_LED_PIN, LOW);
      digitalWrite(IR_LED_PIN, LOW);
      break;
    case IR_ON:
      digitalWrite(RED_LED_PIN, LOW);
      digitalWrite(IR_LED_PIN, HIGH);
      break;
    case DARK2:
      digitalWrite(RED_LED_PIN, LOW);
      digitalWrite(IR_LED_PIN, LOW);
      break;
  }
}

const char* phaseName(PulseOxPhase phase) {
  switch (phase) {
    case RED_ON:
      return "RED_ON";
    case DARK1:
      return "DARK1";
    case IR_ON:
      return "IR_ON";
    case DARK2:
      return "DARK2";
  }
  return "UNKNOWN";
}

void writeMetadata() {
  Serial.println("META,lab,PULSEOX_REFERENCE");
  Serial.println("META,acq_class,PHASED_CYCLE");
  Serial.println("META,adc_resolution_bits,14");
  Serial.println("META,cycle_rate_hz,100");
  Serial.println("META,phase_rate_hz,400");
  Serial.println("META,selected_ports,A0,A1,A2,A3");
  Serial.println("META,pulseox_analog_map,reflective_raw=A0,transmission_raw=A1,reflective_filtered=A2,transmission_filtered=A3");
  Serial.println("META,pulseox_led_pins,IR_D5,RED_D6");
  Serial.println("META,pulseox_phase_sequence,RED_ON,DARK1,IR_ON,DARK2");
  Serial.println("META,phase_fields,t_us,cycle_idx,phase,reflective_raw,transmission_raw,reflective_filtered,transmission_filtered");
  Serial.println("META,cycle_fields,t_us,cycle_idx,reflective_raw_red_corr,reflective_raw_ir_corr,transmission_raw_red_corr,transmission_raw_ir_corr,reflective_filtered_red_corr,reflective_filtered_ir_corr,transmission_filtered_red_corr,transmission_filtered_ir_corr");
}

int readSettledPulseOxChannel(int analogPin) {
  analogRead(analogPin);

  long accumulatedValue = 0;
  for (int sampleIndex = 0; sampleIndex < ADC_SETTLED_SAMPLE_COUNT; ++sampleIndex) {
    accumulatedValue += analogRead(analogPin);
  }

  return static_cast<int>(accumulatedValue / ADC_SETTLED_SAMPLE_COUNT);
}

void emitPhasePacket(unsigned long timestampUs) {
  Serial.print("PHASE,");
  Serial.print(timestampUs);
  Serial.print(",");
  Serial.print(currentCycleIndex);
  Serial.print(",");
  Serial.print(phaseName(currentPhase));

  for (int index = 0; index < ANALOG_INPUT_COUNT; ++index) {
    Serial.print(",");
    Serial.print(phaseSamples[currentPhase][index]);
  }

  Serial.println();
}

void emitCyclePacket(unsigned long timestampUs) {
  const long reflectiveRawRedCorrected = phaseSamples[RED_ON][REFLECTIVE_RAW] - phaseSamples[DARK1][REFLECTIVE_RAW];
  const long reflectiveRawIrCorrected = phaseSamples[IR_ON][REFLECTIVE_RAW] - phaseSamples[DARK2][REFLECTIVE_RAW];
  const long transmissionRawRedCorrected = phaseSamples[RED_ON][TRANSMISSION_RAW] - phaseSamples[DARK1][TRANSMISSION_RAW];
  const long transmissionRawIrCorrected = phaseSamples[IR_ON][TRANSMISSION_RAW] - phaseSamples[DARK2][TRANSMISSION_RAW];
  const long reflectiveFilteredRedCorrected = phaseSamples[RED_ON][REFLECTIVE_FILTERED] - phaseSamples[DARK1][REFLECTIVE_FILTERED];
  const long reflectiveFilteredIrCorrected = phaseSamples[IR_ON][REFLECTIVE_FILTERED] - phaseSamples[DARK2][REFLECTIVE_FILTERED];
  const long transmissionFilteredRedCorrected = phaseSamples[RED_ON][TRANSMISSION_FILTERED] - phaseSamples[DARK1][TRANSMISSION_FILTERED];
  const long transmissionFilteredIrCorrected = phaseSamples[IR_ON][TRANSMISSION_FILTERED] - phaseSamples[DARK2][TRANSMISSION_FILTERED];

  Serial.print("CYCLE,");
  Serial.print(timestampUs);
  Serial.print(",");
  Serial.print(currentCycleIndex);
  Serial.print(",");
  Serial.print(reflectiveRawRedCorrected);
  Serial.print(",");
  Serial.print(reflectiveRawIrCorrected);
  Serial.print(",");
  Serial.print(transmissionRawRedCorrected);
  Serial.print(",");
  Serial.print(transmissionRawIrCorrected);
  Serial.print(",");
  Serial.print(reflectiveFilteredRedCorrected);
  Serial.print(",");
  Serial.print(reflectiveFilteredIrCorrected);
  Serial.print(",");
  Serial.print(transmissionFilteredRedCorrected);
  Serial.print(",");
  Serial.print(transmissionFilteredIrCorrected);
  Serial.println();
}

void captureCurrentPhase(unsigned long timestampUs) {
  for (int index = 0; index < ANALOG_INPUT_COUNT; ++index) {
    phaseSamples[currentPhase][index] = readSettledPulseOxChannel(ANALOG_INPUT_PINS[index]);
  }

  emitPhasePacket(timestampUs);

  if (currentPhase == DARK2) {
    emitCyclePacket(timestampUs);
    currentCycleIndex += 1;
  }
}

void advancePhase() {
  currentPhase = static_cast<PulseOxPhase>((currentPhase + 1) % PHASE_COUNT);
  applyPulseOxPhase();
}

void setup() {
  Serial.begin(BAUD_RATE);

  while (!Serial && millis() < 3000) {
  }

  analogReadResolution(ADC_RESOLUTION_BITS);
  pinMode(IR_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  applyPulseOxPhase();
  writeMetadata();
  nextPhaseCaptureUs = micros() + PHASE_PERIOD_US;
}

void loop() {
  const unsigned long nowUs = micros();
  if ((long)(nowUs - nextPhaseCaptureUs) < 0) {
    return;
  }

  captureCurrentPhase(nowUs);
  advancePhase();
  nextPhaseCaptureUs += PHASE_PERIOD_US;
}
