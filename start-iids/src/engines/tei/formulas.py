"""TEI-J pure formulas (Technological Exergy Impact, Joule-based).

Spec ref: `docs/sources/..._Implementation_Spec_v1.0.md` sec. 14 and Appendix A,
cross-checked against "Manuale operativo – Modulo TEI-J (beta) per EEA+" (repo
root PDF) — ADR-018 supersedes ADR-011 items 1-3 for this module: that ADR was
written believing the SRC-TEI manual had no machine-readable text in this
corpus, but the PDF was present in the repo root all along (ADR-018).

Everything in this module is now DOC (confirmed against the real manual):
exergy conversions, MTS/MTO loss (sec. 3-5 / manual §3-5), backlog with its
N_man=0 / N_sold>N_man guards (manual §5.3), the f_tech aggregation (manual
§6.3), the quality-penalty ratio formula (manual §4.4/5.4, `compute_quality_penalty`
docstring — corrected from an earlier ARCH guess, see ADR-018), and the MTO
powder-pricing / B_TILE identifications (manual §3: `Ex_SDU = m_SDU * b_SD`,
`Ex_T = N_T^man * b_T`, confirming this module's `B_SDM`/`B_TILE` coefficient
choices were already right).

Still open (ADR-018, not fabricated here): the manual's quality-penalty sum
runs over multiple parameters k with a dedicated `Quality` fact table (manual
§8.3); this module's single-parameter case is what sec. 14.2's minimal MTS/MTO
dataset actually carries. And per Appendix M, a confirmed *formula* is not the
same as an *approved coefficient value* — B_TILE/B_SDM/KAPPA_MTS/KAPPA_MTO
numeric values remain DRAFT/test-only pending the project owner's sign-off on
an actual `dim_coefficient` set (ADR-011 item 4 tracks a separate, unrelated
open item: cluster-trend thresholds).
"""
from __future__ import annotations

from dataclasses import dataclass

from src.core.coefficients import CoefficientSet
from src.core.units.energy import exergy_from_mass, gas_nm3_to_mj, kwh_to_mj
from src.engines.errors import EngineError, ErrorCategory


@dataclass(frozen=True)
class MTSFlow:
    """Minimal MTS (push, spray-dryer / body-preparation area) dataset, sec. 14.1."""

    m_rm_kg: float
    m_uw_kg: float
    m_sdm_kg: float
    e_sd_kwh: float
    t_prod_h: float
    q_mts: float | None = None  # measured quality metric feeding sec. 14.7


@dataclass(frozen=True)
class MTOFlow:
    """Minimal MTO (pull, forming + kiln + finishing) dataset, sec. 14.2."""

    m_sdu_kg: float
    n_t_man: float
    n_t_sold: float
    e_form_kwh: float
    e_kiln_nm3: float
    t_prod_h: float
    q_mto: float | None = None


@dataclass(frozen=True)
class MTSExergy:
    ex_rm_mj: float
    ex_uw_mj: float
    ex_e_sd_mj: float
    ex_sdm_mj: float
    ex_loss_mts_mj: float


@dataclass(frozen=True)
class MTOExergy:
    ex_sdm_used_mj: float
    ex_e_form_mj: float
    ex_e_kiln_mj: float
    ex_t_mj: float
    ex_loss_mto_mj: float


def _require_non_negative(value: float, field_name: str, record_key: str) -> None:
    if value < 0:
        raise EngineError(
            ErrorCategory.PHYSICAL_RANGE_ERROR,
            f"'{field_name}' must not be negative, got {value}",
            record_key=record_key,
        )


def compute_mts_exergy(flow: MTSFlow, coefficients: CoefficientSet, record_key: str) -> MTSExergy:
    """Sec. 14.3-14.4: Ex_x = q_x * b_x; Ex_el[MJ] = kWh * 3.6;
    Ex_loss^MTS = (Ex_RM + Ex_UW + Ex_E,SD) - Ex_SDM."""
    for name, value in (("m_rm_kg", flow.m_rm_kg), ("m_uw_kg", flow.m_uw_kg), ("m_sdm_kg", flow.m_sdm_kg)):
        _require_non_negative(value, name, record_key)

    b_rm = coefficients.get("B_RM").value
    b_uw = coefficients.get("B_UW").value
    b_sdm = coefficients.get("B_SDM").value

    ex_rm = exergy_from_mass(flow.m_rm_kg, b_rm)
    ex_uw = exergy_from_mass(flow.m_uw_kg, b_uw)
    ex_e_sd = kwh_to_mj(flow.e_sd_kwh)
    ex_sdm = exergy_from_mass(flow.m_sdm_kg, b_sdm)
    ex_loss_mts = (ex_rm + ex_uw + ex_e_sd) - ex_sdm

    return MTSExergy(
        ex_rm_mj=ex_rm, ex_uw_mj=ex_uw, ex_e_sd_mj=ex_e_sd, ex_sdm_mj=ex_sdm,
        ex_loss_mts_mj=ex_loss_mts,
    )


def compute_mto_exergy(flow: MTOFlow, coefficients: CoefficientSet, record_key: str) -> MTOExergy:
    """Sec. 14.3, 14.5: Ex_loss^MTO = (Ex_SDM + Ex_E,form + Ex_E,kiln) - Ex_T.

    ARCH note: the minimal MTO dataset (sec. 14.2) carries `m_SDU` (powder used),
    not `m_SDM`; this implementation prices the powder entering the MTO stage as
    `m_sdu_kg * b_SDM` (same atomized-powder material, same specific exergy
    coefficient as its MTS output) — pending SRC-TEI confirmation.
    """
    for name, value in (("m_sdu_kg", flow.m_sdu_kg), ("n_t_man", flow.n_t_man), ("n_t_sold", flow.n_t_sold)):
        _require_non_negative(value, name, record_key)

    b_sdm = coefficients.get("B_SDM").value
    b_tile = coefficients.get("B_TILE").value  # ARCH — see module docstring
    pci_gas = coefficients.get("PCI_GAS").value
    f_ex_gas = coefficients.get("F_EX_GAS").value

    ex_sdm_used = exergy_from_mass(flow.m_sdu_kg, b_sdm)
    ex_e_form = kwh_to_mj(flow.e_form_kwh)
    ex_e_kiln = gas_nm3_to_mj(flow.e_kiln_nm3, pci_gas, f_ex_gas)
    ex_t = exergy_from_mass(flow.n_t_man, b_tile)
    ex_loss_mto = (ex_sdm_used + ex_e_form + ex_e_kiln) - ex_t

    return MTOExergy(
        ex_sdm_used_mj=ex_sdm_used, ex_e_form_mj=ex_e_form, ex_e_kiln_mj=ex_e_kiln,
        ex_t_mj=ex_t, ex_loss_mto_mj=ex_loss_mto,
    )


def compute_backlog(flow: MTOFlow, ex_t_mj: float, record_key: str) -> tuple[float, list[str]]:
    """Sec. 14.6: Ex_inv = (1 - N_sold/N_man) * Ex_T.

    Protections (DOC, not to be relaxed): N_man == 0 rejects the calc run for the
    group; N_sold > N_man in the same period raises the TEMPORAL_MISMATCH flag —
    the value is NOT clamped automatically, so a negative Ex_inv is preserved.
    """
    if flow.n_t_man == 0:
        raise EngineError(
            ErrorCategory.CALCULATION_ERROR,
            "N_man = 0: TEI backlog is undefined for this group, run rejected",
            record_key=record_key,
        )
    flags: list[str] = []
    if flow.n_t_sold > flow.n_t_man:
        flags.append("TEMPORAL_MISMATCH")
    ex_inv = (1.0 - (flow.n_t_sold / flow.n_t_man)) * ex_t_mj
    return ex_inv, flags


def compute_quality_penalty(
    q: float | None, q_target: float | None, kappa: float | None, exposed_exergy_mj: float,
    record_key: str = "",
) -> float:
    """Sec. 14.7 (MTS4/MTO4) — DOC, confirmed verbatim against "Manuale operativo
    – Modulo TEI-J (beta) per EEA+" sec. 4.4/5.4 (ADR-018, supersedes ADR-011 item 1):

        Ex_qual = kappa * max(0, 1 - q / q_target) * Ex_exposed

    A *ratio* shortfall against a target/acceptability value `q_target` (the
    manual's q-bar), not the absolute-difference shortfall `max(0, q_thr - q)`
    this module used before the manual became available — the two are only
    equivalent when q is already normalized to a [0, 1] scale with q_target=1,
    which sec. 14.2's minimal dataset never guaranteed. `q_target` corresponds
    to the `Q_THR_MTS`/`Q_THR_MTO` coefficients (name unchanged to avoid an
    unrelated config/schema churn); "threshold" there means this ratio's
    denominator, not a subtraction reference point.

    The manual sums this term over multiple quality parameters k (its own
    kappa_k per parameter); this module still handles the single-parameter
    case (K={1}) sec. 14.2's minimal MTS/MTO dataset carries — a true
    per-parameter sum needs a `Quality` fact table (manual sec. 8.3) this
    schema doesn't have yet, tracked as a follow-up, not fabricated here.

    Any missing input yields zero penalty ("not measured", never an implicit
    pass/fail judgement call).
    """
    if q is None or q_target is None or kappa is None:
        return 0.0
    if q_target <= 0:
        raise EngineError(
            ErrorCategory.PHYSICAL_RANGE_ERROR,
            f"q_target must be > 0 (it is a ratio denominator), got {q_target}",
            record_key=record_key,
        )
    shortfall = max(0.0, 1.0 - (q / q_target))
    return kappa * shortfall * exposed_exergy_mj


def compute_f_tech(
    ex_loss_base_mts_mj: float,
    ex_loss_base_mto_mj: float,
    ex_loss_mts_mj: float,
    ex_loss_mto_mj: float,
    ex_inv_mj: float,
    ex_qual_mts_mj: float,
    ex_qual_mto_mj: float,
) -> float:
    """Sec. 14.8, verbatim DOC formula."""
    return (
        (ex_loss_base_mts_mj + ex_loss_base_mto_mj)
        - (ex_loss_mts_mj + ex_loss_mto_mj)
        - ex_inv_mj
        - ex_qual_mts_mj
        - ex_qual_mto_mj
    )
