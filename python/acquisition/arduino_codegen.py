from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from acquisition.gui_models import PULSEOX_ROLE_RED, validate_signal_configurations
from acquisition.presets import get_preset, is_phased_cycle_preset


REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATED_ARDUINO_SKETCH_DIR = REPO_ROOT / "data" / "generated_arduino_sketches"
DEFAULT_FALLBACK_RATE_HZ = 120


@dataclass(frozen=True, slots=True)
class GeneratedSketchArtifact:
    sketch_dir: Path
    sketch_path: Path
    acquisition_class: str
    sample_rate_hz: int
    sample_period_us: int
    analog_ports: tuple[str, ...]
    uses_pulseox_led_cycle: bool
    phase_rate_hz: int | None = None
    cycle_rate_hz: int | None = None


def _timestamp_tag() -> str:
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


def _sanitize_comment_text(text: str) -> str:
    return text.replace("\n", " ").replace("\r", " ").strip()


def _escape_cpp_string(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def _signal_rate_hz(signal_configuration) -> int:
    preset = get_preset(signal_configuration.preset_name)
    return preset.default_sample_rate_hz or preset.default_cycle_rate_hz or DEFAULT_FALLBACK_RATE_HZ


def determine_generated_sample_rate_hz(signal_configurations) -> int:
    rates = [_signal_rate_hz(signal_configuration) for signal_configuration in signal_configurations]
    return max(rates, default=DEFAULT_FALLBACK_RATE_HZ)


def uses_pulseox_led_cycle(signal_configurations) -> bool:
    return any(is_phased_cycle_preset(signal_configuration.preset_name) for signal_configuration in signal_configurations)


def determine_generated_acquisition_class(signal_configurations) -> str:
    if uses_pulseox_led_cycle(signal_configurations):
        return "PHASED_CYCLE"

    sample_rate_hz = determine_generated_sample_rate_hz(signal_configurations)
    return "CONT_HIGH" if sample_rate_hz > 500 else "CONT_MED"


def _pulseox_role_value(signal_configuration) -> str:
    return signal_configuration.pulseox_role


def _render_metadata_block(
    signal_configurations,
    acquisition_class: str,
    sample_rate_hz: int,
    analog_ports: tuple[str, ...],
    pulseox_led_cycle: bool,
) -> str:
    selected_ports_csv = ",".join(analog_ports)

    if pulseox_led_cycle:
        cycle_rate_hz = sample_rate_hz
        phase_rate_hz = cycle_rate_hz * 4
        phase_fields_csv = ",".join(("t_us", "cycle_idx", "phase", *analog_ports))
        cycle_fields_csv = ",".join(("t_us", "cycle_idx", *(signal.name.strip() for signal in signal_configurations)))
        role_csv = ",".join(_pulseox_role_value(signal_configuration) for signal_configuration in signal_configurations)
        return "\n".join(
            (
                '  Serial.println("META,lab,GUI_SELECTED_SIGNALS");',
                f'  Serial.println("META,acq_class,{acquisition_class}");',
                f'  Serial.println("META,rate_hz,{cycle_rate_hz}");',
                f'  Serial.println("META,cycle_rate_hz,{cycle_rate_hz}");',
                f'  Serial.println("META,phase_rate_hz,{phase_rate_hz}");',
                f'  Serial.println("META,phase_fields,{_escape_cpp_string(phase_fields_csv)}");',
                f'  Serial.println("META,cycle_fields,{_escape_cpp_string(cycle_fields_csv)}");',
                f'  Serial.println("META,selected_ports,{selected_ports_csv}");',
                f'  Serial.println("META,pulseox_signal_roles,{role_csv}");',
                '  Serial.println("META,pulseox_led_pins,IR_D5,RED_D6");',
                '  Serial.println("META,pulseox_phase_sequence,RED_ON,DARK1,IR_ON,DARK2");',
            )
        )

    fields_csv = ",".join(("t_ms", *analog_ports))
    return "\n".join(
        (
            '  Serial.println("META,lab,GUI_SELECTED_SIGNALS");',
            f'  Serial.println("META,acq_class,{acquisition_class}");',
            f'  Serial.println("META,rate_hz,{sample_rate_hz}");',
            f'  Serial.println("META,fields,{fields_csv}");',
            f'  Serial.println("META,selected_ports,{selected_ports_csv}");',
        )
    )


def _render_continuous_sketch(signal_configurations, baud_rate: int) -> str:
    sample_rate_hz = determine_generated_sample_rate_hz(signal_configurations)
    sample_period_us = max(1, round(1_000_000 / sample_rate_hz))
    analog_ports = tuple(signal_configuration.analog_port for signal_configuration in signal_configurations)
    acquisition_class = determine_generated_acquisition_class(signal_configurations)
    selected_signal_comments = "\n".join(
        f"//   {signal_configuration.analog_port} -> {_sanitize_comment_text(signal_configuration.name)}"
        f" [{signal_configuration.preset_name}]"
        for signal_configuration in signal_configurations
    )
    fields_csv = ",".join(("t_ms", *analog_ports))
    analog_input_constants = ", ".join(analog_ports)
    metadata_block = _render_metadata_block(
        signal_configurations=signal_configurations,
        acquisition_class=acquisition_class,
        sample_rate_hz=sample_rate_hz,
        analog_ports=analog_ports,
        pulseox_led_cycle=False,
    )

    return f"""// Generated by the Biomedical Instrumentation Lab GUI.
//
// This sketch is generated from the currently selected GUI signals.
// Highest selected preset rate: {sample_rate_hz} Hz.
// Selected signals:
{selected_signal_comments}
//
// Shared protocol packets:
//   META,lab,GUI_SELECTED_SIGNALS
//   META,acq_class,{acquisition_class}
//   META,rate_hz,{sample_rate_hz}
//   META,fields,{fields_csv}
//   DATA,{fields_csv}

const unsigned long BAUD_RATE = {baud_rate};
const unsigned long SAMPLE_RATE_HZ = {sample_rate_hz};
const unsigned long SAMPLE_PERIOD_US = {sample_period_us};

const int ANALOG_INPUT_PINS[] = {{{analog_input_constants}}};
const int ANALOG_INPUT_COUNT = sizeof(ANALOG_INPUT_PINS) / sizeof(ANALOG_INPUT_PINS[0]);

unsigned long nextSampleTimeUs = 0;

void writeMetadata() {{
{metadata_block}
}}

void setup() {{
  Serial.begin(BAUD_RATE);

  while (!Serial && millis() < 3000) {{
  }}

  writeMetadata();
  nextSampleTimeUs = micros();
}}

void loop() {{
  const unsigned long nowUs = micros();
  if ((long)(nowUs - nextSampleTimeUs) < 0) {{
    return;
  }}

  nextSampleTimeUs += SAMPLE_PERIOD_US;

  Serial.print("DATA,");
  Serial.print(millis());

  for (int index = 0; index < ANALOG_INPUT_COUNT; ++index) {{
    Serial.print(",");
    Serial.print(analogRead(ANALOG_INPUT_PINS[index]));
  }}

  Serial.println();
}}
"""


def _render_pulseox_sketch(signal_configurations, baud_rate: int) -> str:
    cycle_rate_hz = determine_generated_sample_rate_hz(signal_configurations)
    cycle_period_us = max(1, round(1_000_000 / cycle_rate_hz))
    phase_period_us = max(1, round(cycle_period_us / 4))
    analog_ports = tuple(signal_configuration.analog_port for signal_configuration in signal_configurations)
    selected_signal_comments = "\n".join(
        f"//   {signal_configuration.analog_port} -> {_sanitize_comment_text(signal_configuration.name)}"
        f" [{signal_configuration.preset_name}, {_pulseox_role_value(signal_configuration)}]"
        for signal_configuration in signal_configurations
    )
    analog_input_constants = ", ".join(analog_ports)
    role_constants = ", ".join("0" if _pulseox_role_value(signal_configuration) == PULSEOX_ROLE_RED else "1" for signal_configuration in signal_configurations)
    metadata_block = _render_metadata_block(
        signal_configurations=signal_configurations,
        acquisition_class="PHASED_CYCLE",
        sample_rate_hz=cycle_rate_hz,
        analog_ports=analog_ports,
        pulseox_led_cycle=True,
    )

    return f"""// Generated by the Biomedical Instrumentation Lab GUI.
//
// This sketch runs in PHASED_CYCLE mode for PulseOx.
// It logs raw phase measurements and one corrected cycle value per configured signal.
// Cycle rate: {cycle_rate_hz} Hz.
// Phase rate: {cycle_rate_hz * 4} Hz.
// Selected signals:
{selected_signal_comments}
//
// Phase order:
//   RED_ON -> DARK1 -> IR_ON -> DARK2
// D6 controls the red LED and D5 controls the IR LED.
//
// Shared protocol packets:
//   META,phase_fields,t_us,cycle_idx,phase,{",".join(analog_ports)}
//   PHASE,t_us,cycle_idx,phase,{",".join(analog_ports)}
//   META,cycle_fields,t_us,cycle_idx,{",".join(_sanitize_comment_text(signal.name) for signal in signal_configurations)}
//   CYCLE,t_us,cycle_idx,<corrected values in configured signal order>

const unsigned long BAUD_RATE = {baud_rate};
const unsigned long CYCLE_RATE_HZ = {cycle_rate_hz};
const unsigned long CYCLE_PERIOD_US = {cycle_period_us};
const unsigned long PHASE_PERIOD_US = {phase_period_us};

const int IR_LED_PIN = 5;
const int RED_LED_PIN = 6;
const int PHASE_COUNT = 4;

const int ANALOG_INPUT_PINS[] = {{{analog_input_constants}}};
const int ANALOG_INPUT_COUNT = sizeof(ANALOG_INPUT_PINS) / sizeof(ANALOG_INPUT_PINS[0]);

// 0 means RED corrected output, 1 means IR corrected output.
const int SIGNAL_ROLE_CODES[] = {{{role_constants}}};

enum PulseOxPhase {{
  RED_ON = 0,
  DARK1 = 1,
  IR_ON = 2,
  DARK2 = 3,
}};

PulseOxPhase currentPhase = RED_ON;
unsigned long nextPhaseCaptureUs = 0;
unsigned long currentCycleIndex = 0;
int phaseSamples[PHASE_COUNT][ANALOG_INPUT_COUNT];

void applyPulseOxPhase() {{
  switch (currentPhase) {{
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
  }}
}}

const char* phaseName(PulseOxPhase phase) {{
  switch (phase) {{
    case RED_ON:
      return "RED_ON";
    case DARK1:
      return "DARK1";
    case IR_ON:
      return "IR_ON";
    case DARK2:
      return "DARK2";
  }}
  return "UNKNOWN";
}}

void writeMetadata() {{
{metadata_block}
}}

void emitPhasePacket(unsigned long timestampUs) {{
  Serial.print("PHASE,");
  Serial.print(timestampUs);
  Serial.print(",");
  Serial.print(currentCycleIndex);
  Serial.print(",");
  Serial.print(phaseName(currentPhase));

  for (int index = 0; index < ANALOG_INPUT_COUNT; ++index) {{
    Serial.print(",");
    Serial.print(phaseSamples[currentPhase][index]);
  }}

  Serial.println();
}}

void emitCyclePacket(unsigned long timestampUs) {{
  Serial.print("CYCLE,");
  Serial.print(timestampUs);
  Serial.print(",");
  Serial.print(currentCycleIndex);

  for (int index = 0; index < ANALOG_INPUT_COUNT; ++index) {{
    const long darkBaseline = (phaseSamples[DARK1][index] + phaseSamples[DARK2][index]) / 2;
    const long redCorrected = phaseSamples[RED_ON][index] - darkBaseline;
    const long irCorrected = phaseSamples[IR_ON][index] - darkBaseline;
    const long correctedValue = SIGNAL_ROLE_CODES[index] == 0 ? redCorrected : irCorrected;

    Serial.print(",");
    Serial.print(correctedValue);
  }}

  Serial.println();
}}

void captureCurrentPhase(unsigned long timestampUs) {{
  for (int index = 0; index < ANALOG_INPUT_COUNT; ++index) {{
    phaseSamples[currentPhase][index] = analogRead(ANALOG_INPUT_PINS[index]);
  }}

  emitPhasePacket(timestampUs);

  if (currentPhase == DARK2) {{
    emitCyclePacket(timestampUs);
    currentCycleIndex += 1;
  }}
}}

void advancePhase() {{
  currentPhase = static_cast<PulseOxPhase>((currentPhase + 1) % PHASE_COUNT);
  applyPulseOxPhase();
}}

void setup() {{
  Serial.begin(BAUD_RATE);

  while (!Serial && millis() < 3000) {{
  }}

  pinMode(IR_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  applyPulseOxPhase();
  writeMetadata();
  nextPhaseCaptureUs = micros() + PHASE_PERIOD_US;
}}

void loop() {{
  const unsigned long nowUs = micros();
  if ((long)(nowUs - nextPhaseCaptureUs) < 0) {{
    return;
  }}

  captureCurrentPhase(nowUs);
  advancePhase();
  nextPhaseCaptureUs += PHASE_PERIOD_US;
}}
"""


def render_generated_analog_capture_sketch(signal_configurations, baud_rate: int) -> str:
    if uses_pulseox_led_cycle(signal_configurations):
        return _render_pulseox_sketch(signal_configurations, baud_rate)
    return _render_continuous_sketch(signal_configurations, baud_rate)


def create_generated_analog_capture_sketch(signal_configurations, baud_rate: int) -> GeneratedSketchArtifact:
    validate_signal_configurations(tuple(signal_configurations))

    timestamp = _timestamp_tag()
    sketch_name = f"generated_arduino_code_{timestamp}"
    sketch_dir = GENERATED_ARDUINO_SKETCH_DIR / sketch_name
    suffix = 1
    while sketch_dir.exists():
        sketch_name = f"generated_arduino_code_{timestamp}_{suffix}"
        sketch_dir = GENERATED_ARDUINO_SKETCH_DIR / sketch_name
        suffix += 1

    sketch_dir.mkdir(parents=True, exist_ok=False)
    sketch_path = sketch_dir / f"{sketch_name}.ino"
    sketch_path.write_text(
        render_generated_analog_capture_sketch(signal_configurations, baud_rate),
        encoding="utf-8",
    )

    sample_rate_hz = determine_generated_sample_rate_hz(signal_configurations)
    sample_period_us = max(1, round(1_000_000 / sample_rate_hz))
    analog_ports = tuple(signal_configuration.analog_port for signal_configuration in signal_configurations)
    pulseox_led_cycle = uses_pulseox_led_cycle(signal_configurations)
    acquisition_class = determine_generated_acquisition_class(signal_configurations)

    return GeneratedSketchArtifact(
        sketch_dir=sketch_dir,
        sketch_path=sketch_path,
        acquisition_class=acquisition_class,
        sample_rate_hz=sample_rate_hz,
        sample_period_us=sample_period_us,
        analog_ports=analog_ports,
        uses_pulseox_led_cycle=pulseox_led_cycle,
        phase_rate_hz=sample_rate_hz * 4 if pulseox_led_cycle else None,
        cycle_rate_hz=sample_rate_hz if pulseox_led_cycle else None,
    )
