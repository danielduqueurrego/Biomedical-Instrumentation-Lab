"""Tests for shared CSV packet parsing helpers."""

from __future__ import annotations

import pytest

from acquisition.protocol import (
    PACKET_TYPE_CYCLE,
    PACKET_TYPE_DATA,
    PACKET_TYPE_PHASE,
    PacketParseError,
    parse_csv_packet,
    parse_cycle_packet,
    parse_data_packet,
    parse_phase_packet,
)


def test_parse_csv_packet_accepts_valid_data_line(protocol_lines, host_timestamp) -> None:
    host_iso, host_unix = host_timestamp
    packet = parse_csv_packet(protocol_lines["data_valid"], host_iso, host_unix)

    assert packet.packet_type == PACKET_TYPE_DATA
    assert packet.payload == ("1523", "512", "487", "530")


@pytest.mark.parametrize("line_key", ["unknown_prefix", "short_data"])
def test_parse_csv_packet_rejects_invalid_lines(line_key, protocol_lines, host_timestamp) -> None:
    host_iso, host_unix = host_timestamp

    with pytest.raises(PacketParseError):
        parse_csv_packet(protocol_lines[line_key], host_iso, host_unix)


def test_parse_data_packet_accepts_valid_line(protocol_lines, host_timestamp) -> None:
    host_iso, host_unix = host_timestamp
    csv_packet = parse_csv_packet(protocol_lines["data_valid"], host_iso, host_unix)

    data_packet = parse_data_packet(csv_packet, expected_field_names=("t_ms", "A0", "A1", "A2"))

    assert data_packet.device_time_ms == 1523
    assert data_packet.values == (512, 487, 530)


@pytest.mark.parametrize(
    ("line_key", "expected_fields"),
    [
        ("data_non_integer", ("t_ms", "A0", "A1", "A2")),
        ("data_valid", ("t_ms", "A0", "A1")),
    ],
)
def test_parse_data_packet_rejects_invalid_payloads(line_key, expected_fields, protocol_lines, host_timestamp) -> None:
    host_iso, host_unix = host_timestamp
    csv_packet = parse_csv_packet(protocol_lines[line_key], host_iso, host_unix)

    with pytest.raises(PacketParseError):
        parse_data_packet(csv_packet, expected_field_names=expected_fields)


def test_parse_phase_packet_accepts_valid_line(protocol_lines, host_timestamp) -> None:
    host_iso, host_unix = host_timestamp
    csv_packet = parse_csv_packet(protocol_lines["phase_valid"], host_iso, host_unix)

    phase_packet = parse_phase_packet(csv_packet, expected_field_names=("A0", "A1", "A2"))

    assert phase_packet.phase_name == "RED_ON"
    assert phase_packet.cycle_index == 312
    assert phase_packet.values == (1842, 1760, 1901)


@pytest.mark.parametrize("line_key", ["phase_unknown", "data_valid"])
def test_parse_phase_packet_rejects_invalid_lines(line_key, protocol_lines, host_timestamp) -> None:
    host_iso, host_unix = host_timestamp
    csv_packet = parse_csv_packet(protocol_lines[line_key], host_iso, host_unix)

    with pytest.raises(PacketParseError):
        parse_phase_packet(csv_packet, expected_field_names=("A0", "A1", "A2"))


def test_parse_cycle_packet_accepts_valid_line(protocol_lines, host_timestamp) -> None:
    host_iso, host_unix = host_timestamp
    csv_packet = parse_csv_packet(protocol_lines["cycle_valid"], host_iso, host_unix)

    cycle_packet = parse_cycle_packet(csv_packet, expected_field_names=("sig_red", "sig_ir", "sig_aux"))

    assert cycle_packet.device_time_us == 127550
    assert cycle_packet.cycle_index == 312
    assert cycle_packet.values == (1721, 1645, 1688)


@pytest.mark.parametrize("line_key", ["cycle_bad_value", "phase_valid"])
def test_parse_cycle_packet_rejects_invalid_lines(line_key, protocol_lines, host_timestamp) -> None:
    host_iso, host_unix = host_timestamp
    csv_packet = parse_csv_packet(protocol_lines[line_key], host_iso, host_unix)

    with pytest.raises(PacketParseError):
        parse_cycle_packet(csv_packet, expected_field_names=("sig_red", "sig_ir", "sig_aux"))
