# ADR-005 — MJ internal, GJ output (P0 mandatory correction)

**Status:** P0 mandatory correction (spec sec. 61), APPLIED

## Context
The -J manuals (TEI/EFA/EcoFA/SFA) label intermediate values as MJ in worked
examples but divide by `1e9` to reach GJ — a defect, since `1e9` only converts
J→GJ, not MJ→GJ.

## Decision
Freeze: computational canonical unit = **MJ**, reporting unit = **GJ**,
`gj = mj / 1000.0`. Never `mj / 1e9`.

## Consequences
`src/core/units/energy.py::mj_to_gj` is the single implementation; every engine
converts through it. `tests/unit/test_units_energy.py` is a mandatory, standalone
regression gate (`test_mj_to_gj`, `test_mj_to_gj_is_not_j_to_gj`).
