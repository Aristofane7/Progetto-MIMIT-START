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
    for key in ("meta", "kpi", "dims", "rows", "clusters", "channels", "quality", "building_placeholder"):
        assert key in payload
    assert payload["meta"]["dataset_label"] == "TEST_LABEL"
    assert payload["kpi"]["record_count"] == len(payload["rows"])


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
