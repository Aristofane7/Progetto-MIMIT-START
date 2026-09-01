"""Unit tests for the generic Edge collector (issue #3, ADR-021, sec. 34.1)."""
import pathlib

import pytest

from src.engines.errors import Severity
from src.ingestion.contracts import load_contract
from src.ingestion.edge.collector import collect

CONTRACT_PATH = (
    pathlib.Path(__file__).resolve().parents[2]
    / "config" / "source_mappings" / "mes_production_v1.yaml"
)


@pytest.fixture()
def contract():
    return load_contract(CONTRACT_PATH)


def test_valid_records_are_accepted_and_renamed_to_target_fields(contract):
    raw = [{"lot_code": "L1", "product_code": "P1", "start_time": "2026-01-01T00:00:00", "output_m2": 10}]
    batch = collect(contract, raw)
    assert batch.accepted == [
        {"lot_id": "L1", "product_id": "P1", "output_m2": 10, "start_time": "2026-01-01T00:00:00"}
    ]
    assert batch.rejected == []


def test_records_missing_a_required_field_are_rejected_not_dropped_silently(contract):
    raw = [{"lot_code": "L1", "product_code": None, "start_time": "2026-01-01T00:00:00"}]
    batch = collect(contract, raw)
    assert batch.accepted == []
    assert len(batch.rejected) == 1
    assert batch.rejected[0].severity == Severity.BLOCKER


def test_duplicate_records_in_the_same_batch_are_deduplicated(contract):
    raw = [
        {"lot_code": "L1", "product_code": "P1", "start_time": "2026-01-01T00:00:00", "output_m2": 10},
        {"lot_code": "L1", "product_code": "P1", "start_time": "2026-01-01T00:00:00", "output_m2": 999},
    ]
    batch = collect(contract, raw)
    assert len(batch.accepted) == 1
    assert batch.accepted[0]["output_m2"] == 10  # first-seen wins, no error


def test_preprocess_hook_runs_before_validation(contract):
    raw = [{"lot_code": "l1", "product_code": "p1", "start_time": "2026-01-01T00:00:00"}]
    batch = collect(contract, raw, preprocess=lambda r: {**r, "lot_code": r["lot_code"].upper()})
    assert batch.accepted[0]["lot_id"] == "L1"


def test_mixed_batch_partitions_correctly(contract):
    raw = [
        {"lot_code": "L1", "product_code": "P1", "start_time": "2026-01-01T00:00:00"},
        {"lot_code": "L2", "product_code": None, "start_time": "2026-01-01T00:00:00"},
    ]
    batch = collect(contract, raw)
    assert len(batch.accepted) == 1
    assert len(batch.rejected) == 1
    assert batch.contract_id == "MES_PRODUCTION_V1"
