from __future__ import annotations

import importlib
import importlib.metadata
from dataclasses import dataclass

from acquisition.arduino_cli_wrapper import ArduinoCli


REQUIRED_MODULES = (
    ("tkinter", None, "GUI support"),
    ("matplotlib", "matplotlib", "live plotting"),
    ("serial", "pyserial", "serial communication"),
)


@dataclass(frozen=True, slots=True)
class PackageCheck:
    module_name: str
    installed: bool
    version: str
    description: str
    error_message: str = ""


@dataclass(frozen=True, slots=True)
class ArduinoCliCheck:
    available: bool
    version: str
    error_message: str = ""


@dataclass(frozen=True, slots=True)
class SerialPortCheck:
    ports: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SystemCheckReport:
    package_checks: tuple[PackageCheck, ...]
    arduino_cli_check: ArduinoCliCheck
    serial_port_check: SerialPortCheck

    @property
    def all_required_items_ready(self) -> bool:
        packages_ready = all(check.installed for check in self.package_checks)
        return packages_ready and self.arduino_cli_check.available


def _detect_package_version(distribution_name: str | None) -> str:
    if not distribution_name:
        return "stdlib"

    try:
        return importlib.metadata.version(distribution_name)
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def check_required_packages() -> tuple[PackageCheck, ...]:
    results = []

    for module_name, distribution_name, description in REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)
        except Exception as error:
            results.append(
                PackageCheck(
                    module_name=module_name,
                    installed=False,
                    version="missing",
                    description=description,
                    error_message=str(error),
                )
            )
            continue

        results.append(
            PackageCheck(
                module_name=module_name,
                installed=True,
                version=_detect_package_version(distribution_name),
                description=description,
            )
        )

    return tuple(results)


def check_arduino_cli() -> ArduinoCliCheck:
    try:
        cli = ArduinoCli.from_environment()
    except FileNotFoundError as error:
        return ArduinoCliCheck(available=False, version="missing", error_message=str(error))

    try:
        version = cli.version()
    except Exception as error:
        return ArduinoCliCheck(available=False, version="error", error_message=str(error))

    return ArduinoCliCheck(available=True, version=version)


def check_serial_ports() -> SerialPortCheck:
    try:
        list_ports_module = importlib.import_module("serial.tools.list_ports")
    except Exception:
        return SerialPortCheck(ports=())

    ports = tuple(f"{port.device} - {port.description}" for port in list_ports_module.comports())
    return SerialPortCheck(ports=ports)


def run_system_check() -> SystemCheckReport:
    return SystemCheckReport(
        package_checks=check_required_packages(),
        arduino_cli_check=check_arduino_cli(),
        serial_port_check=check_serial_ports(),
    )


def render_system_check(report: SystemCheckReport) -> str:
    lines = ["Biomedical Instrumentation Lab system check", ""]
    lines.append("Python packages:")
    for check in report.package_checks:
        status = "OK" if check.installed else "MISSING"
        detail = f"{check.module_name} ({check.description})"
        if check.installed:
            lines.append(f"  [{status}] {detail} - {check.version}")
        else:
            lines.append(f"  [{status}] {detail} - {check.error_message}")

    lines.append("")
    lines.append("Arduino CLI:")
    if report.arduino_cli_check.available:
        lines.append(f"  [OK] {report.arduino_cli_check.version}")
    else:
        lines.append(f"  [MISSING] {report.arduino_cli_check.error_message}")

    lines.append("")
    lines.append("Serial ports:")
    if report.serial_port_check.ports:
        lines.append(f"  [OK] {len(report.serial_port_check.ports)} port(s) detected")
        for port in report.serial_port_check.ports:
            lines.append(f"  - {port}")
    else:
        lines.append("  [WARN] No serial ports detected")

    lines.append("")
    overall = "READY" if report.all_required_items_ready else "SETUP NEEDED"
    lines.append(f"Overall status: {overall}")
    return "\n".join(lines)


def main() -> int:
    report = run_system_check()
    print(render_system_check(report))
    return 0 if report.all_required_items_ready else 1
