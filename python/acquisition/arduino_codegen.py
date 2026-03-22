from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from acquisition.presets import get_preset


REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATED_ARDUINO_SKETCH_DIR = REPO_ROOT / "data" / "generated_arduino_sketches"
DEFAULT_FALLBACK_RATE_HZ = 120


@dataclass(frozen=True, slots=True)
class GeneratedSketchArtifact:
    sketch_dir: Path
    sketch_path: Path
    sample_rate_hz: int
    sample_period_us: int
    analog_ports: tuple[str, ...]
    uses_pulseox_led_cycle: bool


def _timestamp_tag() -> str:
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


def _sanitize_comment_text(text: str) -> str:
    return text.replace("\n", " ").replace("\r", " ").strip()


def _signal_rate_hz(signal_configuration) -> int:
    preset = get_preset(signal_configuration.preset_name)
    return preset.default_sample_rate_hz or preset.default_cycle_rate_hz or DEFAULT_FALLBACK_RATE_HZ


def determine_generated_sample_rate_hz(signal_configurations) -> int:
    rates = [_signal_rate_hz(signal_configuration) for signal_configuration in signal_configurations]
    return max(rates, default=DEFAULT_FALLBACK_RATE_HZ)


def determine_generated_acquisition_class(signal_configurations) -> str:
    sample_rate_hz = determine_generated_sample_rate_hz(signal_configurations)
    return "CONT_HIGH" if sample_rate_hz > 500 else "CONT_MED"


def uses_pulseox_led_cycle(signal_configurations) -> bool:
    return any(signal_configuration.preset_name == "PulseOx" for signal_configuration in signal_configurations)


def _render_metadata_block(
    acquisition_class: str,
    sample_rate_hz: int,
    fields_csv: str,
    selected_ports_csv: str,
    pulseox_led_cycle: bool,
) -> str:
    lines = [
        '  Serial.println("META,lab,GUI_SELECTED_SIGNALS");',
        f'  Serial.println("META,acq_class,{acquisition_class}");',
        f'  Serial.println("META,rate_hz,{sample_rate_hz}");',
        f'  Serial.println("META,fields,{fields_csv}");',
        f'  Serial.println("META,selected_ports,{selected_ports_csv}");',
    ]
    if pulseox_led_cycle:
        lines.extend(
            (
                '  Serial.println("META,pulseox_led_pins,IR_D5,RED_D6");',
                '  Serial.println("META,pulseox_phase_sequence,RED_ON,DARK1,IR_ON,DARK2");',
            )
        )
    return "\n".join(lines)


def render_generated_analog_capture_sketch(signal_configurations, baud_rate: int) -> str:
    sample_rate_hz = determine_generated_sample_rate_hz(signal_configurations)
    sample_period_us = max(1, round(1_000_000 / sample_rate_hz))
    analog_ports = tuple(signal_configuration.analog_port for signal_configuration in signal_configurations)
    acquisition_class = determine_generated_acquisition_class(signal_configurations)
    pulseox_led_cycle = uses_pulseox_led_cycle(signal_configurations)
    phase_period_us = max(1, round(sample_period_us / 4))

    selected_signal_comments = "\n".join(
        f"//   {signal_configuration.analog_port} -> {_sanitize_comment_text(signal_configuration.name)}"
        f" [{signal_configuration.preset_name}]"
        for signal_configuration in signal_configurations
    )
    selected_ports_csv = ",".join(analog_ports)
    fields_csv = ",".join(("t_ms", *analog_ports))
    analog_input_constants = ", ".join(analog_ports)

    pulseox_comment_block = (
        "// PulseOx preset detected.\n"
        "// The generated sketch drives a four-phase LED cycle:\n"
        "//   RED_ON -> DARK1 -> IR_ON -> DARK2\n"
        "// D6 controls the red LED and D5 controls the IR LED.\n"
        if pulseox_led_cycle
        else ""
    )
    pulseox_constants_block = (
        f"""
const int IR_LED_PIN = 5;
const int RED_LED_PIN = 6;
const int PHASE_COUNT = 4;
const unsigned long PHASE_PERIOD_US = {phase_period_us};

enum PulseOxPhase {{
  RED_ON = 0,
  DARK1 = 1,
  IR_ON = 2,
  DARK2 = 3,
}};
"""
        if pulseox_led_cycle
        else ""
    )
    pulseox_state_block = (
        """
PulseOxPhase currentPhase = RED_ON;

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
"""
        if pulseox_led_cycle
        else ""
    )
    pulseox_setup_block = (
        """
  pinMode(IR_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  applyPulseOxPhase();
"""
        if pulseox_led_cycle
        else ""
    )
    pulseox_loop_block = (
        """
  if ((long)(nowUs - nextSampleTimeUs) < 0) {
    return;
  }

  nextSampleTimeUs += PHASE_PERIOD_US;
  currentPhase = static_cast<PulseOxPhase>((currentPhase + 1) % PHASE_COUNT);
  applyPulseOxPhase();

  if (currentPhase != RED_ON) {
    return;
  }
"""
        if pulseox_led_cycle
        else f"""
  if ((long)(nowUs - nextSampleTimeUs) < 0) {{
    return;
  }}

  nextSampleTimeUs += SAMPLE_PERIOD_US;
"""
    )

    metadata_block = _render_metadata_block(
        acquisition_class=acquisition_class,
        sample_rate_hz=sample_rate_hz,
        fields_csv=fields_csv,
        selected_ports_csv=selected_ports_csv,
        pulseox_led_cycle=pulseox_led_cycle,
    )

    return f"""// Generated by the Biomedical Instrumentation Lab GUI.
//
// This sketch is generated from the currently selected GUI signals.
// Highest selected preset rate: {sample_rate_hz} Hz.
// Selected signals:
{selected_signal_comments}
{pulseox_comment_block}//
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
{pulseox_constants_block}
unsigned long nextSampleTimeUs = 0;
{pulseox_state_block}
void writeMetadata() {{
{metadata_block}
}}

void setup() {{
  Serial.begin(BAUD_RATE);

  while (!Serial && millis() < 3000) {{
  }}
{pulseox_setup_block}
  writeMetadata();
  nextSampleTimeUs = micros();
}}

void loop() {{
  const unsigned long nowUs = micros();
{pulseox_loop_block}
  const unsigned long tMs = millis();

  Serial.print("DATA,");
  Serial.print(tMs);

  for (int index = 0; index < ANALOG_INPUT_COUNT; ++index) {{
    Serial.print(",");
    Serial.print(analogRead(ANALOG_INPUT_PINS[index]));
  }}

  Serial.println();
}}
"""


def create_generated_analog_capture_sketch(signal_configurations, baud_rate: int) -> GeneratedSketchArtifact:
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

    return GeneratedSketchArtifact(
        sketch_dir=sketch_dir,
        sketch_path=sketch_path,
        sample_rate_hz=sample_rate_hz,
        sample_period_us=sample_period_us,
        analog_ports=analog_ports,
        uses_pulseox_led_cycle=pulseox_led_cycle,
    )
