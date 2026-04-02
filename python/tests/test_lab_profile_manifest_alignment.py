"""Guardrail tests to keep manifest, presets, and GUI profile defaults aligned."""

from __future__ import annotations

from acquisition.protocol import PULSEOX_ANALOG_PORTS
from acquisition.lab_manifest import LAB_MANIFEST
from acquisition.lab_profiles import CUSTOM_LAB_PROFILE_NAME, LAB_PROFILE_ORDER, LAB_PROFILES
from acquisition.presets import LAB_PRESETS


def test_manifest_entries_map_to_gui_profiles_and_presets() -> None:
    for lab_name, manifest_entry in LAB_MANIFEST.items():
        assert manifest_entry.profile_label in LAB_PROFILES, (
            f"Manifest profile label {manifest_entry.profile_label!r} is missing in LAB_PROFILES."
        )
        assert lab_name in LAB_PRESETS, f"Manifest lab {lab_name!r} is missing in LAB_PRESETS."


def test_lab_profile_order_matches_manifest_profile_labels() -> None:
    manifest_profile_labels = tuple(entry.profile_label for entry in LAB_MANIFEST.values())

    assert LAB_PROFILE_ORDER[0] == CUSTOM_LAB_PROFILE_NAME
    assert LAB_PROFILE_ORDER[1:] == manifest_profile_labels
    assert set(LAB_PROFILE_ORDER[1:]) == set(LAB_PROFILES)


def test_all_lab_profile_signal_presets_exist_in_lab_presets() -> None:
    for profile_label, profile in LAB_PROFILES.items():
        for signal in profile.signal_configurations:
            assert signal.preset_name in LAB_PRESETS, (
                f"Profile {profile_label!r} references unknown preset {signal.preset_name!r}."
            )


def test_pulseox_profile_uses_fixed_four_channel_mapping() -> None:
    pulseox_profile = LAB_PROFILES["Pulse Oximetry"]

    assert len(pulseox_profile.signal_configurations) == len(PULSEOX_ANALOG_PORTS)
    assert tuple(signal.analog_port for signal in pulseox_profile.signal_configurations) == PULSEOX_ANALOG_PORTS
