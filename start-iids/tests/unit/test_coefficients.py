import pytest

from src.core.coefficients import Coefficient, CoefficientSet
from src.engines.errors import EngineError, ErrorCategory


def _approved_set():
    return CoefficientSet(
        coefficient_set_id="COEFF_2026_01",
        status="APPROVED",
        coefficients={
            "B_EL": Coefficient(
                coefficient_id="B_EL", domain="TEI", code="B_EL", value=1.0,
                unit="MJ/kWh", confidence="A",
            )
        },
    )


def test_get_returns_coefficient_from_approved_set():
    coeff = _approved_set().get("B_EL")
    assert coeff.value == 1.0


def test_draft_set_is_rejected_even_if_code_exists():
    draft = CoefficientSet(
        coefficient_set_id="COEFF_DRAFT",
        status="DRAFT",
        coefficients={
            "B_EL": Coefficient(
                coefficient_id="B_EL", domain="TEI", code="B_EL", value=1.0,
                unit="MJ/kWh", confidence="A",
            )
        },
    )
    with pytest.raises(EngineError) as exc:
        draft.get("B_EL")
    assert exc.value.category == ErrorCategory.MISSING_COEFFICIENT


def test_missing_code_raises_missing_coefficient():
    with pytest.raises(EngineError) as exc:
        _approved_set().get("UNKNOWN_CODE")
    assert exc.value.category == ErrorCategory.MISSING_COEFFICIENT


def test_invalid_confidence_rejected():
    with pytest.raises(ValueError):
        Coefficient(
            coefficient_id="X", domain="TEI", code="X", value=1.0, unit="MJ", confidence="Z",
        )
