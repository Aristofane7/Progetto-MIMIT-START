"""Data contract loading and validation. Spec ref: sec. 27.

Rule (sec. 27, last line): "Nessun agente deve codificare mapping direttamente
dentro il business engine." Field mapping/renaming, required-field policy and
dedup keys live exclusively in YAML contracts under `config/source_mappings/`,
loaded through this module — never hardcoded inside an ingestion script or, worse,
inside a calculation engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.engines.errors import DataQualityFinding, Severity


@dataclass(frozen=True)
class TimestampSpec:
    field: str
    timezone: str


@dataclass(frozen=True)
class FieldSpec:
    source_field: str
    target: str
    type: str
    required: bool = False
    unit: str | None = None
    min: float | None = None
    max: float | None = None


@dataclass(frozen=True)
class DataContract:
    contract_id: str
    source_system: str
    entity: str
    owner: str
    keys: list[str]
    timestamp: TimestampSpec
    fields: dict[str, FieldSpec]
    reject_if_missing: list[str]
    dedup_key: list[str]


def load_contract(path: str | Path) -> DataContract:
    raw = yaml.safe_load(Path(path).read_text())
    fields = {
        name: FieldSpec(
            source_field=name,
            target=spec["target"],
            type=spec["type"],
            required=spec.get("required", False),
            unit=spec.get("unit"),
            min=spec.get("min"),
            max=spec.get("max"),
        )
        for name, spec in raw["fields"].items()
    }
    return DataContract(
        contract_id=raw["contract_id"],
        source_system=raw["source_system"],
        entity=raw["entity"],
        owner=raw["owner"],
        keys=list(raw["keys"]),
        timestamp=TimestampSpec(**raw["timestamp"]),
        fields=fields,
        reject_if_missing=list(raw.get("quality", {}).get("reject_if_missing", [])),
        dedup_key=list(raw.get("deduplication", {}).get("key", [])),
    )


def validate_record(record: dict[str, Any], contract: DataContract) -> list[DataQualityFinding]:
    """Sec. 27/29: returns BLOCKER findings for any `reject_if_missing` field that
    is absent or None. Does not mutate or coerce the record."""
    findings: list[DataQualityFinding] = []
    for required_field in contract.reject_if_missing:
        if record.get(required_field) in (None, ""):
            findings.append(
                DataQualityFinding(
                    dataset_name=contract.contract_id,
                    record_key=str(compute_dedup_key(record, contract)),
                    check_code="missing_required_field",
                    severity=Severity.BLOCKER,
                    passed=False,
                    observed_value=None,
                    expected_rule=f"'{required_field}' must not be missing/empty",
                )
            )
    return findings


def compute_dedup_key(record: dict[str, Any], contract: DataContract) -> tuple[Any, ...]:
    """Sec. 33 idempotence: natural/dedup key as declared by the contract."""
    return tuple(record.get(k) for k in contract.dedup_key)
