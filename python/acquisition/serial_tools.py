import serial
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo


DEFAULT_BAUD_RATE = 230400
DEFAULT_TIMEOUT_S = 0.25


def list_available_ports() -> list[ListPortInfo]:
    return sorted(list(list_ports.comports()), key=lambda port: port.device)


def format_port_choices(ports: list[ListPortInfo]) -> str:
    return "\n".join(f"  - {port.device}: {port.description}" for port in ports)


def choose_serial_port(requested_port: str | None) -> str:
    ports = list_available_ports()
    devices = {port.device for port in ports}

    if requested_port:
        if requested_port in devices or not ports:
            return requested_port

        raise RuntimeError(
            "The requested serial port was not found.\n"
            f"Requested: {requested_port}\n"
            "Available ports:\n"
            f"{format_port_choices(ports)}"
        )

    if not ports:
        raise RuntimeError("No serial ports were detected.")

    if len(ports) == 1:
        return ports[0].device

    raise RuntimeError(
        "Multiple serial ports were detected. Re-run the app with --port and pick one of these:\n"
        f"{format_port_choices(ports)}"
    )


def open_serial_connection(port: str, baud_rate: int = DEFAULT_BAUD_RATE) -> serial.Serial:
    return serial.Serial(port=port, baudrate=baud_rate, timeout=DEFAULT_TIMEOUT_S)
