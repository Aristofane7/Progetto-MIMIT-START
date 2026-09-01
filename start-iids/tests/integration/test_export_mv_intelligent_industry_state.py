"""The Power BI semantic model's local/dev data source (issue #8, ADR-016)
is these CSVs — this test guards that the export keeps working and keeps
exposing the columns the model depends on (esp. the process passthrough,
ADR-016, needed for the Factory page's drill-down).
"""
import csv

from scripts.export_mv_intelligent_industry_state import build_synthetic_engine, export


def test_export_writes_fact_and_dimension_csvs(tmp_path):
    engine = build_synthetic_engine()
    counts = export(engine, tmp_path)

    assert counts["fact_shadow_state"] >= 24
    assert counts["dim_process"] > 0
    assert counts["dim_product"] > 0

    with (tmp_path / "fact_shadow_state.csv").open(newline="") as f:
        header = next(csv.reader(f))
    for required in ("plant_id", "line_id", "process_id", "process_name", "tsi_norm", "p_tsi_5",
                      "data_quality_score", "calc_run_id"):
        assert required in header
