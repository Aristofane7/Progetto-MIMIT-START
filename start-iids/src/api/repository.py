"""Read-only data access for the Digital Shadow API. Spec ref: sec. 37, 46.

Uses SQLAlchemy Core (portable across the PostgreSQL-compatible reference and
Azure SQL, sec. 5) with parameterized, read-only queries. No method in this class
performs an INSERT/UPDATE/DELETE — the API layer is read-only by construction
(sec. 3.2, 37.5).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

# Historical replay pattern, spec sec. 46: latest row with source/period timestamp
# <= :at, ordered descending. Every query in this module follows this shape.


class IIDSRepository:
    def __init__(self, engine: Engine):
        self._engine = engine

    def get_factory_state(self, plant_id: str, at: datetime) -> dict[str, Any] | None:
        query = text(
            """
            SELECT * FROM fact_eea_state
            WHERE plant_id = :plant_id AND period_start <= :at
            ORDER BY period_start DESC
            LIMIT 1
            """
        )
        with self._engine.connect() as conn:
            row = conn.execute(query, {"plant_id": plant_id, "at": at}).mappings().first()
        return dict(row) if row else None

    def get_product_state(self, product_id: str, at: datetime) -> dict[str, Any] | None:
        query = text(
            """
            SELECT p.product_id, p.cluster_id, p.cluster_version, s.*
            FROM dim_product p
            LEFT JOIN fact_ptsa_state s
                ON s.product_id = p.product_id AND s.period_start <= :at
            WHERE p.product_id = :product_id
            ORDER BY s.period_start DESC
            LIMIT 1
            """
        )
        with self._engine.connect() as conn:
            row = conn.execute(query, {"product_id": product_id, "at": at}).mappings().first()
        return dict(row) if row else None

    def get_lot_state(self, lot_id: str, at: datetime) -> dict[str, Any] | None:
        query = text(
            """
            SELECT
                lot.lot_id, lot.product_id, lot.plant_id, lot.start_ts, lot.end_ts,
                prod.cluster_id, prod.cluster_version,
                eea.f_env_gj, eea.f_econ_gj, eea.f_soc_gj, eea.f_tech_gj,
                eea.sa_gj, eea.tsi_norm,
                ptsa.p_tsi_z, ptsa.p_tsi_5, ptsa.tii
            FROM fact_production_lot lot
            LEFT JOIN dim_product prod ON prod.product_id = lot.product_id
            LEFT JOIN fact_eea_state eea
                ON eea.lot_id = lot.lot_id AND eea.period_start <= :at
            LEFT JOIN fact_ptsa_state ptsa
                ON ptsa.lot_id = lot.lot_id AND ptsa.period_start <= :at
            WHERE lot.lot_id = :lot_id
            ORDER BY eea.period_start DESC, ptsa.period_start DESC
            LIMIT 1
            """
        )
        with self._engine.connect() as conn:
            row = conn.execute(query, {"lot_id": lot_id, "at": at}).mappings().first()
        return dict(row) if row else None

    def get_industry_state(
        self, plant_id: str | None, product_id: str | None, at: datetime
    ) -> list[dict[str, Any]]:
        conditions = ["period_start <= :at"]
        params: dict[str, Any] = {"at": at}
        if plant_id is not None:
            conditions.append("plant_id = :plant_id")
            params["plant_id"] = plant_id
        if product_id is not None:
            conditions.append("product_id = :product_id")
            params["product_id"] = product_id

        query = text(
            f"""
            SELECT * FROM mv_intelligent_industry_state
            WHERE {' AND '.join(conditions)}
            ORDER BY period_start DESC
            """
        )
        with self._engine.connect() as conn:
            rows = conn.execute(query, params).mappings().all()
        return [dict(r) for r in rows]
