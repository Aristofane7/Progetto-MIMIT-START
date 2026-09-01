"""Read-only Digital Shadow API. Spec ref: sec. 37.

HARD CONSTRAINT (sec. 3.2, 37.5): this module must never define a route that
writes to the physical system or accepts an actuation command. Only GET routes
are declared. CI greps the whole `src/` tree for the forbidden write-route
patterns listed in sec. 3.2 of the implementation spec and fails the build if any
are found (see `.github/workflows/ci.yml`) — deliberately not spelled out
verbatim here, so this compliance note itself never trips that same guard.
"""
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import Depends, FastAPI, HTTPException, Query

from src.api.repository import IIDSRepository

app = FastAPI(
    title="START Intelligent Industry Digital Shadow API",
    version="1.0.0",
    description="Read-only API. No actuation endpoint exists or will be added in v1.",
)

_repository: IIDSRepository | None = None


def configure_repository(repository: IIDSRepository) -> None:
    """Wires the app to a repository instance (e.g. built from a SQLAlchemy Engine
    pointed at the production database). Call once at process start-up."""
    global _repository
    _repository = repository


def get_repository() -> IIDSRepository:
    if _repository is None:
        raise RuntimeError("IIDSRepository not configured; call configure_repository() first")
    return _repository


@app.get("/api/v1/shadow/factory")
def get_factory_shadow(
    plant_id: str,
    at: datetime | None = Query(default=None),
    repo: IIDSRepository = Depends(get_repository),
):
    at = at or datetime.now(UTC)
    state = repo.get_factory_state(plant_id, at)
    if state is None:
        raise HTTPException(status_code=404, detail=f"no EEA+ state found for plant '{plant_id}' at {at}")
    return {"plant_id": plant_id, "at": at.isoformat(), "eea": state}


@app.get("/api/v1/shadow/product/{product_id}")
def get_product_shadow(
    product_id: str,
    at: datetime | None = Query(default=None),
    repo: IIDSRepository = Depends(get_repository),
):
    at = at or datetime.now(UTC)
    state = repo.get_product_state(product_id, at)
    if state is None:
        raise HTTPException(status_code=404, detail=f"product '{product_id}' not found")
    return {"product_id": product_id, "at": at.isoformat(), "ptsa": state}


@app.get("/api/v1/shadow/lot/{lot_id}")
def get_lot_shadow(
    lot_id: str,
    at: datetime | None = Query(default=None),
    repo: IIDSRepository = Depends(get_repository),
):
    at = at or datetime.now(UTC)
    state = repo.get_lot_state(lot_id, at)
    if state is None:
        raise HTTPException(status_code=404, detail=f"lot '{lot_id}' not found")
    return {"lot_id": lot_id, "at": at.isoformat(), "state": state}


@app.get("/api/v1/shadow/industry")
def get_industry_shadow(
    plant_id: str | None = None,
    product_id: str | None = None,
    at: datetime | None = Query(default=None),
    repo: IIDSRepository = Depends(get_repository),
):
    at = at or datetime.now(UTC)
    rows = repo.get_industry_state(plant_id, product_id, at)
    return {"plant_id": plant_id, "product_id": product_id, "at": at.isoformat(), "results": rows}
