"""Product cluster catalog with SCD Type 2 versioning.

Spec ref: sec. 19.6 ("nuova versione cluster NON sovrascrive quella storica"),
sec. 51 (SCD2 for cluster assignment). Rule (sec. 19.6): re-clustering is not run
automatically on a schedule in v1 — versions are imported/approved on request.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductCluster:
    cluster_id: int
    cluster_version: str
    cqs: float | None = None


class ClusterCatalog:
    """In-memory mirror of `dim_product_cluster` SCD2 semantics."""

    def __init__(self) -> None:
        self._by_id_version: dict[tuple[int, str], ProductCluster] = {}
        self._current_version_by_id: dict[int, str] = {}

    def add_version(self, cluster: ProductCluster, *, make_current: bool = True) -> None:
        key = (cluster.cluster_id, cluster.cluster_version)
        if key in self._by_id_version:
            raise ValueError(
                f"cluster_version '{cluster.cluster_version}' already exists for "
                f"cluster_id {cluster.cluster_id}; versions are immutable once added"
            )
        self._by_id_version[key] = cluster
        if make_current:
            self._current_version_by_id[cluster.cluster_id] = cluster.cluster_version

    def current(self, cluster_id: int) -> ProductCluster | None:
        version = self._current_version_by_id.get(cluster_id)
        if version is None:
            return None
        return self._by_id_version[(cluster_id, version)]

    def history(self, cluster_id: int) -> list[ProductCluster]:
        return [c for (cid, _), c in self._by_id_version.items() if cid == cluster_id]

    def is_current(self, cluster_id: int, cluster_version: str) -> bool:
        return self._current_version_by_id.get(cluster_id) == cluster_version
