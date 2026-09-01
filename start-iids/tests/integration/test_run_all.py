"""Integration test for `python3 -m src.run_all` (spec: the source workbook's own
regeneration instruction)."""
import csv

from src.run_all import run


def test_run_all_produces_rows_for_every_plant_year():
    rows = run()
    plants_years = {(r["plant"], r["year"]) for r in rows}
    assert plants_years == {
        ("D020", 2023), ("D020", 2024), ("D020", 2025),
        ("D060", 2023), ("D060", 2024), ("D060", 2025),
        ("D240", 2023), ("D240", 2024), ("D240", 2025),
    }


def test_run_all_includes_tsi_rel_only_for_2025():
    rows = run()
    tsi_rel_rows = [r for r in rows if r["variable"] == "tsi_rel"]
    assert {r["year"] for r in tsi_rel_rows} == {2025}
    assert {r["plant"] for r in tsi_rel_rows} == {"D020", "D060", "D240"}


def test_run_all_writes_csv(tmp_path):
    output_path = tmp_path / "calculation_log.csv"
    rows = run(output_path)
    assert output_path.exists()
    with output_path.open() as f:
        written_rows = list(csv.DictReader(f))
    assert len(written_rows) == len(rows)
