# Hardware Validation

> Practical bench-check workflow for instructors and TAs.

Use this section when a board, firmware path, or classroom station needs a quick known-good check before or during a lab session.

---

## Start Here

The goal is to keep validation simple and repeatable.

For every validation run, record at least:

- target sample rate or cycle rate
- achieved rate from the saved CSV
- test duration
- malformed or parse-error count
- packet loss notes
- plot responsiveness notes
- hardware notes

---

## Quick Workflow

1. open the matching lab guide from [docs/labs/](../labs/README.md)
2. load the matching GUI lab profile or session preset
3. compile and upload firmware
4. run a short acquisition, usually `30` to `60` seconds
5. save the session CSV
6. fill the per-lab validation table immediately after the run
7. add screenshots or wiring photos only if they help explain a result

---

## What To Use

- general checklist: [hardware_validation_checklist_template.md](./hardware_validation_checklist_template.md)
- short per-lab tables: [lab_validation_tables.md](./lab_validation_tables.md)
- example CSV layout: [examples/session_csv/README.md](../../examples/session_csv/README.md)

---

## How To Estimate Achieved Rate

### Continuous labs

Use the `DATA` rows in the session CSV.

Simple estimate:

- `achieved_rate_hz = (sample_count - 1) / ((last_device_time - first_device_time) / time_scale)`

Use:

- `time_scale = 1_000_000` for `t_us`
- `time_scale = 1_000` for `t_ms`

### PulseOx

Use the `CYCLE` rows for cycle rate, or the `PHASE` rows for raw phase rate.

Simple estimate:

- `achieved_cycle_rate_hz = (cycle_count - 1) / ((last_t_us - first_t_us) / 1_000_000)`

---

## What Counts As A Good Classroom Result

For a short classroom checkout, a run is usually acceptable when:

- the achieved rate is close to the target rate
- malformed packets are zero or very low
- the session CSV is readable without confusion
- the plot updates smoothly enough for students to follow
- there are no unexplained disconnects or port errors

---

## Screenshot Guidance

Screenshots are optional, but they help when:

- a station behaves differently from the others
- a TA needs to show a known-good setup
- the plot looks suspicious during a live run

Place screenshots in [docs/screenshots/](../screenshots/README.md).

---

## See Also

- [Lab guides](../labs/README.md)
- [Student setup](../student_setup.md)
- [Lab validation tables](./lab_validation_tables.md)
- [Example session CSVs](../../examples/session_csv/README.md)
