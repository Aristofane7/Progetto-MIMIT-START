import pathlib

from src.engines.errors import Severity
from src.ingestion.contracts import compute_dedup_key, load_contract, validate_record

CONTRACT_PATH = (
    pathlib.Path(__file__).resolve().parents[2]
    / "config" / "source_mappings" / "mes_production_v1.yaml"
)


def test_load_contract_matches_spec_example():
    contract = load_contract(CONTRACT_PATH)
    assert contract.contract_id == "MES_PRODUCTION_V1"
    assert contract.source_system == "MES"
    assert contract.timestamp.timezone == "Europe/Rome"
    assert contract.dedup_key == ["lot_code", "product_code", "start_time"]
    assert contract.fields["lot_code"].target == "lot_id"


def test_validate_record_passes_when_required_fields_present():
    contract = load_contract(CONTRACT_PATH)
    record = {"lot_code": "L1", "product_code": "P1", "start_time": "2026-01-01T00:00:00", "output_m2": 10}
    assert validate_record(record, contract) == []


def test_validate_record_blocks_missing_required_field():
    contract = load_contract(CONTRACT_PATH)
    record = {"lot_code": "L1", "product_code": None, "start_time": "2026-01-01T00:00:00"}
    findings = validate_record(record, contract)
    assert len(findings) == 1
    assert findings[0].severity == Severity.BLOCKER
    assert findings[0].check_code == "missing_required_field"


def test_dedup_key_matches_contract_declaration():
    contract = load_contract(CONTRACT_PATH)
    record = {"lot_code": "L1", "product_code": "P1", "start_time": "2026-01-01T00:00:00"}
    assert compute_dedup_key(record, contract) == ("L1", "P1", "2026-01-01T00:00:00")
