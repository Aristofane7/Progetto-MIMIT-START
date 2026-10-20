"""The 4 draft contracts added for issue #3/ADR-021 (ERP/HR/SCADA/LIMS) load
correctly and target the exact fields their downstream engine/table expects
-- proving the *shape* is right even though the *source* side is still `TBD_*`
pending P0-03 (real IT field names)."""
import pathlib

import pytest

from src.ingestion.contracts import load_contract

CONFIG_DIR = pathlib.Path(__file__).resolve().parents[2] / "config" / "source_mappings"


@pytest.mark.parametrize("filename,contract_id,source_system", [
    ("erp_economic_v1.yaml", "ERP_ECONOMIC_V1", "ERP"),
    ("hr_social_v1.yaml", "HR_SOCIAL_V1", "HR"),
    ("scada_process_observation_v1.yaml", "SCADA_PROCESS_OBSERVATION_V1", "SCADA"),
    ("lims_quality_v1.yaml", "LIMS_QUALITY_V1", "LIMS"),
])
def test_draft_contract_loads(filename, contract_id, source_system):
    contract = load_contract(CONFIG_DIR / filename)
    assert contract.contract_id == contract_id
    assert contract.source_system == source_system
    assert contract.dedup_key  # every draft declares an idempotence key
    assert contract.reject_if_missing  # every draft rejects at least one missing field


def test_erp_economic_targets_match_ecofa_engine_inputs():
    contract = load_contract(CONFIG_DIR / "erp_economic_v1.yaml")
    targets = {spec.target for spec in contract.fields.values()}
    assert targets == {"accounting_term_id", "amount_eur", "value_added_eur", "fixed_assets_eur"}


def test_hr_social_targets_match_sfa_engine_inputs():
    contract = load_contract(CONFIG_DIR / "hr_social_v1.yaml")
    targets = {spec.target for spec in contract.fields.values()}
    assert targets == {"stakeholder_code", "value_eur", "hours_lost", "hours_training", "em_co2_kg"}


def test_scada_targets_match_fact_process_observation_columns():
    contract = load_contract(CONFIG_DIR / "scada_process_observation_v1.yaml")
    targets = {spec.target for spec in contract.fields.values()}
    assert targets == {"equipment_id", "variable_code", "value_num", "original_unit"}


def test_lims_targets_match_fact_quality_test_columns():
    contract = load_contract(CONFIG_DIR / "lims_quality_v1.yaml")
    targets = {spec.target for spec in contract.fields.values()}
    assert targets == {"lot_id", "test_code", "measured_value", "unit", "acceptance_threshold"}
