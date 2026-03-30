# `PHASED_CYCLE` Firmware

> Committed multi-phase cycle sketches for labs where meaning depends on timing phase.

Use this folder when you need a known committed `PHASED_CYCLE` sketch instead of relying only on the GUI-generated PulseOx path.

---

## 🚀 Start Here

Typical lab:

- PulseOx

Current committed UNO R4 WiFi reference sketch:

- `uno_r4_wifi/pulse_ox_reference`

---

## 🧠 What `PHASED_CYCLE` Means In This Repo

Current expectations:

- use `META`, `PHASE`, and `CYCLE`
- keep the phase order explicit
- sample all required analog channels during each phase
- plot corrected cycle values by default in the GUI

Current PulseOx behavior:

- drive `D6` for RED LED control
- drive `D5` for IR LED control
- step through `RED_ON`, `DARK1`, `IR_ON`, `DARK2`
- sample the same four wired optical channels during every phase:
  - `A0 = reflective_raw`
  - `A1 = transmission_raw`
  - `A2 = reflective_filtered`
  - `A3 = transmission_filtered`
- emit one raw `PHASE` packet per phase
- emit one corrected `CYCLE` packet after `DARK2`

---

## 🔗 See Also

- [PulseOx lab guide](../../docs/labs/pulse_ox.md)
- [Generated firmware workflow](../../docs/generated_firmware_workflow.md)
- [Serial protocol](../../docs/serial_protocol.md)
