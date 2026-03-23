from dataclasses import dataclass


PACKET_TYPE_META = "META"
PACKET_TYPE_DATA = "DATA"
PACKET_TYPE_PHASE = "PHASE"
PACKET_TYPE_CYCLE = "CYCLE"
PACKET_TYPE_STAT = "STAT"
PACKET_TYPE_ERR = "ERR"

SHARED_PACKET_TYPES = (
    PACKET_TYPE_META,
    PACKET_TYPE_DATA,
    PACKET_TYPE_PHASE,
    PACKET_TYPE_CYCLE,
    PACKET_TYPE_STAT,
    PACKET_TYPE_ERR,
)

PACKET_MIN_FIELD_COUNTS = {
    PACKET_TYPE_META: 3,
    PACKET_TYPE_DATA: 3,
    PACKET_TYPE_PHASE: 5,
    PACKET_TYPE_CYCLE: 4,
    PACKET_TYPE_STAT: 4,
    PACKET_TYPE_ERR: 4,
}

UNO_R4_ANALOG_PORTS = ("A0", "A1", "A2", "A3", "A4", "A5")
UNO_R4_ANALOG_BANK_FIELDS = ("t_ms", *UNO_R4_ANALOG_PORTS)
UNO_R4_ANALOG_INDEX = {port_name: index for index, port_name in enumerate(UNO_R4_ANALOG_PORTS)}
PULSEOX_PHASE_NAMES = ("RED_ON", "DARK1", "IR_ON", "DARK2")

# The legacy reference CLI app still plots the first three UNO R4 analog inputs.
DEFAULT_THREE_CHANNEL_FIELDS = ("t_ms", "A0", "A1", "A2")


class PacketParseError(ValueError):
    """Raised when a serial line does not match the shared CSV protocol."""

    def __init__(self, message: str, raw_line: str):
        super().__init__(message)
        self.raw_line = raw_line


@dataclass(slots=True)
class CsvPacket:
    host_time_iso: str
    host_time_unix_s: float
    packet_type: str
    payload: tuple[str, ...]
    raw_line: str


@dataclass(slots=True)
class DataPacket:
    host_time_iso: str
    host_time_unix_s: float
    device_time_ms: int
    field_names: tuple[str, ...]
    values: tuple[int, ...]
    raw_line: str


@dataclass(slots=True)
class PhasePacket:
    host_time_iso: str
    host_time_unix_s: float
    device_time_us: int
    cycle_index: int
    phase_name: str
    field_names: tuple[str, ...]
    values: tuple[int, ...]
    raw_line: str


@dataclass(slots=True)
class CyclePacket:
    host_time_iso: str
    host_time_unix_s: float
    device_time_us: int
    cycle_index: int
    field_names: tuple[str, ...]
    values: tuple[int, ...]
    raw_line: str


def parse_csv_packet(raw_line: str, host_time_iso: str, host_time_unix_s: float) -> CsvPacket:
    fields = tuple(field.strip() for field in raw_line.split(","))
    if not fields or not fields[0]:
        raise PacketParseError("Received an empty packet prefix.", raw_line)

    packet_type = fields[0]
    if packet_type not in SHARED_PACKET_TYPES:
        raise PacketParseError(f"Unknown packet prefix {packet_type!r}.", raw_line)

    min_fields = PACKET_MIN_FIELD_COUNTS[packet_type]
    if len(fields) < min_fields:
        raise PacketParseError(
            f"Packet type {packet_type} requires at least {min_fields} CSV fields, received {len(fields)}.",
            raw_line,
        )

    return CsvPacket(
        host_time_iso=host_time_iso,
        host_time_unix_s=host_time_unix_s,
        packet_type=packet_type,
        payload=fields[1:],
        raw_line=raw_line,
    )


def parse_meta_packet(packet: CsvPacket) -> tuple[str, tuple[str, ...]]:
    if packet.packet_type != PACKET_TYPE_META:
        raise PacketParseError("Expected a META packet.", packet.raw_line)

    key = packet.payload[0]
    values = packet.payload[1:]
    return key, values


def parse_data_packet(packet: CsvPacket, expected_field_names: tuple[str, ...]) -> DataPacket:
    if packet.packet_type != PACKET_TYPE_DATA:
        raise PacketParseError("Expected a DATA packet.", packet.raw_line)

    if expected_field_names[0] != "t_ms":
        raise ValueError("The first expected DATA field must be 't_ms'.")

    if len(packet.payload) != len(expected_field_names):
        raise PacketParseError(
            f"Expected {len(expected_field_names)} DATA payload fields, received {len(packet.payload)}.",
            packet.raw_line,
        )

    try:
        device_time_ms = int(packet.payload[0])
        values = tuple(int(value) for value in packet.payload[1:])
    except ValueError as error:
        raise PacketParseError("DATA payload contains a non-integer value.", packet.raw_line) from error

    if device_time_ms < 0:
        raise PacketParseError("DATA device timestamp must be non-negative.", packet.raw_line)

    return DataPacket(
        host_time_iso=packet.host_time_iso,
        host_time_unix_s=packet.host_time_unix_s,
        device_time_ms=device_time_ms,
        field_names=expected_field_names,
        values=values,
        raw_line=packet.raw_line,
    )


def parse_phase_packet(packet: CsvPacket, expected_field_names: tuple[str, ...]) -> PhasePacket:
    if packet.packet_type != PACKET_TYPE_PHASE:
        raise PacketParseError("Expected a PHASE packet.", packet.raw_line)

    if len(packet.payload) != len(expected_field_names) + 3:
        raise PacketParseError(
            f"Expected {len(expected_field_names) + 3} PHASE payload fields, received {len(packet.payload)}.",
            packet.raw_line,
        )

    try:
        device_time_us = int(packet.payload[0])
        cycle_index = int(packet.payload[1])
        values = tuple(int(value) for value in packet.payload[3:])
    except ValueError as error:
        raise PacketParseError("PHASE payload contains a non-integer value.", packet.raw_line) from error

    phase_name = packet.payload[2]
    if device_time_us < 0 or cycle_index < 0:
        raise PacketParseError("PHASE timestamps and cycle indices must be non-negative.", packet.raw_line)

    if phase_name not in PULSEOX_PHASE_NAMES:
        raise PacketParseError(f"Unknown phase name {phase_name!r}.", packet.raw_line)

    return PhasePacket(
        host_time_iso=packet.host_time_iso,
        host_time_unix_s=packet.host_time_unix_s,
        device_time_us=device_time_us,
        cycle_index=cycle_index,
        phase_name=phase_name,
        field_names=expected_field_names,
        values=values,
        raw_line=packet.raw_line,
    )


def parse_cycle_packet(packet: CsvPacket, expected_field_names: tuple[str, ...]) -> CyclePacket:
    if packet.packet_type != PACKET_TYPE_CYCLE:
        raise PacketParseError("Expected a CYCLE packet.", packet.raw_line)

    if len(packet.payload) != len(expected_field_names) + 2:
        raise PacketParseError(
            f"Expected {len(expected_field_names) + 2} CYCLE payload fields, received {len(packet.payload)}.",
            packet.raw_line,
        )

    try:
        device_time_us = int(packet.payload[0])
        cycle_index = int(packet.payload[1])
        values = tuple(int(value) for value in packet.payload[2:])
    except ValueError as error:
        raise PacketParseError("CYCLE payload contains a non-integer value.", packet.raw_line) from error

    if device_time_us < 0 or cycle_index < 0:
        raise PacketParseError("CYCLE timestamps and cycle indices must be non-negative.", packet.raw_line)

    return CyclePacket(
        host_time_iso=packet.host_time_iso,
        host_time_unix_s=packet.host_time_unix_s,
        device_time_us=device_time_us,
        cycle_index=cycle_index,
        field_names=expected_field_names,
        values=values,
        raw_line=packet.raw_line,
    )
