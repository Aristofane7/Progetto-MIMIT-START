"""Guards config/baselines/rp73_baseline_2022.yaml (issue #9, ADR-017): the
RP7.3 aggregate model has used this baseline since ADR-012, but it had no
governed config artifact until the Stage 9 self-check found the gap. Status
must stay DRAFT until the project owner explicitly signs off (separate from
the ADR-013 coefficient/weight approval)."""
from pathlib import Path

import yaml

BASELINE_FILE = (
    Path(__file__).resolve().parents[2] / "config" / "baselines" / "rp73_baseline_2022.yaml"
)


def test_rp73_baseline_config_has_required_fields():
    raw = yaml.safe_load(BASELINE_FILE.read_text())
    for field in ("baseline_id", "baseline_name", "baseline_year", "functional_unit",
                  "coefficient_set_id", "status"):
        assert field in raw
    assert raw["baseline_year"] == 2022
    assert raw["coefficient_set_id"] == "COEFF_RP73_PROVISIONAL_2026"
    assert raw["status"] in ("DRAFT", "APPROVED", "RETIRED")
