from __future__ import annotations

from acquisition.arduino_cli_wrapper import ArduinoCli
from acquisition.system_check import render_system_check, run_system_check


def main() -> int:
    report = run_system_check()
    print(render_system_check(report))

    if not report.arduino_cli_check.available:
        print("\nBoard detection skipped because Arduino CLI is not available.")
        return 1

    print("\nDetected board ports:")
    try:
        cli = ArduinoCli.from_environment()
        detected = cli.list_detected_boards()
    except Exception as error:
        print(f"  [WARN] Could not list connected boards: {error}")
        return 1 if not report.all_required_items_ready else 0

    if not detected:
        print("  [WARN] No boards detected. Connect your Arduino and run this command again.")
        return 1 if not report.all_required_items_ready else 0

    for item in detected:
        fqbn_text = item.fqbn or "unknown fqbn"
        print(f"  [OK] {item.port} | {item.board_name} | {fqbn_text}")

    return 0 if report.all_required_items_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
