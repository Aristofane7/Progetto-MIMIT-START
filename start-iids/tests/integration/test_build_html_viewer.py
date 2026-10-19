"""Integration test: the HTML viewer build produces a valid single file with
a parseable, correctly-shaped embedded data payload (issue #8, ADR-023).
"""
import json

import pytest

from scripts.build_html_viewer import build_payload, render_html
from scripts.export_mv_intelligent_industry_state import build_synthetic_engine


@pytest.fixture(scope="module")
def payload():
    engine = build_synthetic_engine()
    return build_payload(engine, dataset_label="TEST_LABEL", data_note="test note")


def _embedded_json(html: str) -> dict:
    marker = "const DATA = "
    start = html.index(marker) + len(marker)
    return json.JSONDecoder().raw_decode(html, start)[0]


def test_payload_has_expected_shape(payload):
    for key in ("meta", "kpi", "dims", "rows", "clusters", "channels", "quality",
                "building_placeholder", "glossary", "real_plants", "sources"):
        assert key in payload
    assert payload["meta"]["dataset_label"] == "TEST_LABEL"
    assert payload["kpi"]["record_count"] == len(payload["rows"])


def test_glossary_covers_every_metric_shown_in_the_viewer(payload):
    # ADR-024: every acronym rendered in the template must resolve to a real,
    # spec-grounded definition — never a bare, unexplained acronym.
    for key in ("sa_gj", "tsi_norm", "f_env_gj", "f_econ_gj", "f_soc_gj", "f_tech_gj",
                "ioai", "opi", "tqi", "p_tsi_5", "tii", "channel_concentration_hhi", "scenario",
                "ex_ref_gj", "phi", "psi", "tsi_abs", "tsi_rel"):
        assert key in payload["glossary"]
        assert payload["glossary"][key]["full"]
        assert payload["glossary"][key]["desc"]


def test_real_plants_has_the_three_real_plants(payload):
    # ADR-026: real RP7.3 plant-level data (D020/D060/D240), kept separate
    # from the synthetic per-lot rows — never fabricated, never mixed in.
    plant_ids = {r["plant_id"] for r in payload["real_plants"]}
    assert plant_ids == {"D020", "D060", "D240"}
    assert len(payload["real_plants"]) == 9  # 3 plants x (2023, 2024, 2025)
    d020_2025 = next(r for r in payload["real_plants"] if r["plant_id"] == "D020" and r["year"] == 2025)
    assert d020_2025["partial_period"] is True
    assert d020_2025["months_active"] == 7


def test_sources_lists_only_real_deposited_files(payload):
    # ADR-026/ADR-027: discovered by filename at build time, never hand-typed,
    # including one level into namespaced deliverable folders (RP8.6/, Attivita_7.10/).
    filenames = {s["filename"] for s in payload["sources"]}
    assert filenames  # the repo root has real RP*/Attività* deliverables
    assert "RPX.Y Titolo_Relazione_Parziale_data.docx" not in filenames
    assert "rp_format_reference.docx" not in filenames
    assert all(f.lower().endswith((".pdf", ".docx")) for f in filenames)
    assert "RP7.10_AI_Business_Model.docx" in filenames
    assert "RP8.6_Assessment_Impatto.docx" in filenames
    draft = {s["filename"]: s["draft"] for s in payload["sources"]}
    assert draft["RP 7.9 Report tecnico delle nuove collezioni.draft.docx"] is True
    assert draft["RP 7.6 Report tecnico di adeguamento impianti_31-10-26.docx"] is False


def test_scenario_passthrough_only_has_real_values(payload):
    # ADR-024: scenario is fact_production_lot's own real CURRENT/HISTORICAL
    # flag (sec. 46) — never a fabricated what-if value.
    scenarios = {r["scenario"] for r in payload["rows"] if r["scenario"] is not None}
    assert scenarios <= {"CURRENT", "HISTORICAL"}


def test_channel_shares_sum_to_one(payload):
    shares = [c["share"] for c in payload["channels"] if c["share"] is not None]
    assert shares  # the synthetic dataset always assigns a channel
    assert abs(sum(shares) - 1.0) < 1e-6


def test_render_html_embeds_parseable_matching_payload(payload):
    html = render_html(payload)
    assert "/*__DATA__*/" not in html
    embedded = _embedded_json(html)
    assert embedded["kpi"]["record_count"] == payload["kpi"]["record_count"]
    assert len(embedded["clusters"]) == len(payload["clusters"])


def test_render_html_requires_the_data_marker(tmp_path, monkeypatch, payload):
    import scripts.build_html_viewer as mod

    broken_template = tmp_path / "template.html"
    broken_template.write_text("<html>no marker here</html>")
    monkeypatch.setattr(mod, "TEMPLATE_PATH", broken_template)

    with pytest.raises(ValueError, match="missing"):
        render_html(payload)
