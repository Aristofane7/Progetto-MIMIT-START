# ADR-001 — Digital Shadow, no actuation

**Status:** APPROVED by architecture (spec sec. 61)

## Context
START's Intelligent Industry model (OR6.10) and the E2C architecture (RP6.6) support
both read (Physical→Digital) and, in a later phase, write (Digital→Physical) flows.

## Decision
The v1 release implements a **Digital Shadow** only: `Physical → Digital`. No
endpoint, service, or code path writes to PLC/SCADA or issues a set-point/command.
`ENABLE_ACTUATION` stays hardcoded `false`; forbidden route patterns
(`/plc/write`, `/actuate`, `/setpoint/apply`, `/command/execute`) are grepped for
in CI (`.github/workflows/ci.yml`) and must never appear in `src/`.

## Consequences
Closed-loop control (Digital Twin) is FUTURE and out of scope until a separate,
explicitly approved architecture phase.
