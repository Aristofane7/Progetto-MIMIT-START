"""API integration test: seeds a SQLite-backed schema, then hits every read-only
endpoint (spec sec. 37). Also asserts no actuation route exists (sec. 3.2, 37.5)."""
import glob
import pathlib
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from src.api.app import app, configure_repository
from src.api.repository import IIDSRepository

MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parents[2] / "sql" / "migrations"
VIEWS_DIR = pathlib.Path(__file__).resolve().parents[2] / "sql" / "views"


@pytest.fixture()
def seeded_engine():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
        for path in sorted(glob.glob(str(MIGRATIONS_DIR / "*.sql"))):
            raw = conn.connection.driver_connection
            raw.executescript(pathlib.Path(path).read_text())
        for path in sorted(glob.glob(str(VIEWS_DIR / "*.sql"))):
            raw = conn.connection.driver_connection
            raw.executescript(pathlib.Path(path).read_text())

        conn.execute(text("INSERT INTO dim_plant (plant_id, plant_name) VALUES ('D060', 'Plant D060')"))
        conn.execute(text(
            "INSERT INTO dim_product_cluster (cluster_id, cluster_version, cqs) VALUES (17, 'RP68_2025', 0.78)"
        ))
        conn.execute(text(
            "INSERT INTO dim_product (product_id, product_name, cluster_id, cluster_version) "
            "VALUES ('PROD-1', 'Tile A', 17, 'RP68_2025')"
        ))
        conn.execute(text(
            "INSERT INTO fact_production_lot (lot_id, product_id, plant_id, start_ts, scenario) "
            "VALUES ('LOT-1', 'PROD-1', 'D060', :start_ts, 'CURRENT')"
        ), {"start_ts": datetime(2026, 1, 1, tzinfo=UTC)})
        conn.execute(text(
            "INSERT INTO dim_coefficient_set (coefficient_set_id, status) VALUES ('COEFF_2026_01', 'APPROVED')"
        ))
        conn.execute(text(
            "INSERT INTO dim_baseline (baseline_id, baseline_name, baseline_year, functional_unit, "
            "coefficient_set_id, status) VALUES ('BASELINE_2017', 'Baseline 2017', 2017, 'm2', "
            "'COEFF_2026_01', 'APPROVED')"
        ))
        conn.execute(text(
            "INSERT INTO audit_calc_run (calc_run_id, engine, engine_version, baseline_id, "
            "coefficient_set_id, period_start, period_end, status, started_at) VALUES "
            "('RUN-1', 'EEA', '1.0.0', 'BASELINE_2017', 'COEFF_2026_01', :ps, :pe, 'SUCCESS', :ps)"
        ), {"ps": datetime(2026, 1, 1, tzinfo=UTC), "pe": datetime(2026, 1, 31, tzinfo=UTC)})
        conn.execute(text(
            "INSERT INTO fact_eea_state (eea_state_id, calc_run_id, plant_id, lot_id, period_start, "
            "period_end, scenario, f_env_gj, f_econ_gj, f_soc_gj, f_tech_gj, sa_gj, tsi_norm) VALUES "
            "(1, 'RUN-1', 'D060', 'LOT-1', :ps, :pe, 'CURRENT', 1.0, 0.5, 0.2, 0.3, 2.0, 0.9)"
        ), {"ps": datetime(2026, 1, 1, tzinfo=UTC), "pe": datetime(2026, 1, 31, tzinfo=UTC)})
        conn.execute(text(
            "INSERT INTO fact_ptsa_state (ptsa_state_id, calc_run_id, period_start, period_end, "
            "product_id, lot_id, plant_id, p_tsi_z, p_tsi_5, tii) VALUES "
            "(1, 'RUN-1', :ps, :pe, 'PROD-1', 'LOT-1', 'D060', -0.047, 3.73, NULL)"
        ), {"ps": datetime(2026, 1, 1, tzinfo=UTC), "pe": datetime(2026, 1, 31, tzinfo=UTC)})
    return engine


@pytest.fixture()
def client(seeded_engine):
    configure_repository(IIDSRepository(seeded_engine))
    return TestClient(app)


def test_factory_shadow_returns_latest_state_at_or_before_at(client):
    resp = client.get("/api/v1/shadow/factory", params={"plant_id": "D060", "at": "2026-02-01T00:00:00Z"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["eea"]["tsi_norm"] == 0.9


def test_factory_shadow_404_when_no_state_before_at(client):
    resp = client.get("/api/v1/shadow/factory", params={"plant_id": "D060", "at": "2025-01-01T00:00:00Z"})
    assert resp.status_code == 404


def test_factory_shadow_historical_replay_across_two_periods(seeded_engine):
    """sec. 46: the API must reconstruct the state 'as of' any point in time,
    not just return the single latest row -- prove it with a second, later
    calc_run for the same plant and three distinct `at` values."""
    with seeded_engine.begin() as conn:
        conn.execute(text(
            "INSERT INTO audit_calc_run (calc_run_id, engine, engine_version, baseline_id, "
            "coefficient_set_id, period_start, period_end, status, started_at) VALUES "
            "('RUN-2', 'EEA', '1.0.0', 'BASELINE_2017', 'COEFF_2026_01', :ps, :pe, 'SUCCESS', :ps)"
        ), {"ps": datetime(2026, 2, 1, tzinfo=UTC), "pe": datetime(2026, 2, 28, tzinfo=UTC)})
        conn.execute(text(
            "INSERT INTO fact_eea_state (eea_state_id, calc_run_id, plant_id, lot_id, period_start, "
            "period_end, scenario, f_env_gj, f_econ_gj, f_soc_gj, f_tech_gj, sa_gj, tsi_norm) VALUES "
            "(2, 'RUN-2', 'D060', 'LOT-1', :ps, :pe, 'CURRENT', 1.1, 0.6, 0.2, 0.3, 2.2, 1.05)"
        ), {"ps": datetime(2026, 2, 1, tzinfo=UTC), "pe": datetime(2026, 2, 28, tzinfo=UTC)})

    configure_repository(IIDSRepository(seeded_engine))
    client = TestClient(app)

    before_both = client.get("/api/v1/shadow/factory", params={"plant_id": "D060", "at": "2025-06-01T00:00:00Z"})
    assert before_both.status_code == 404

    between_the_two = client.get("/api/v1/shadow/factory", params={"plant_id": "D060", "at": "2026-01-15T00:00:00Z"})
    assert between_the_two.json()["eea"]["tsi_norm"] == 0.9  # RUN-1, not RUN-2 yet

    after_both = client.get("/api/v1/shadow/factory", params={"plant_id": "D060", "at": "2026-02-15T00:00:00Z"})
    assert after_both.json()["eea"]["tsi_norm"] == 1.05  # RUN-2 now the latest state <= at


def test_product_shadow(client):
    resp = client.get("/api/v1/shadow/product/PROD-1", params={"at": "2026-02-01T00:00:00Z"})
    assert resp.status_code == 200
    assert resp.json()["ptsa"]["p_tsi_5"] == 3.73


def test_lot_shadow_returns_both_eea_and_ptsa(client):
    resp = client.get("/api/v1/shadow/lot/LOT-1", params={"at": "2026-02-01T00:00:00Z"})
    assert resp.status_code == 200
    state = resp.json()["state"]
    assert state["tsi_norm"] == 0.9
    assert state["p_tsi_5"] == 3.73


def test_industry_shadow(client):
    resp = client.get("/api/v1/shadow/industry", params={"plant_id": "D060", "at": "2026-02-01T00:00:00Z"})
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 1


def test_no_actuation_route_exists(client):
    route_paths = {route.path for route in app.routes}
    forbidden = {"/plc/write", "/actuate", "/setpoint/apply", "/command/execute"}
    assert not (route_paths & forbidden)
    for route in app.routes:
        methods = getattr(route, "methods", set()) or set()
        assert "POST" not in methods
        assert "PUT" not in methods
        assert "DELETE" not in methods
        assert "PATCH" not in methods
