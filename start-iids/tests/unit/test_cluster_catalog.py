import pytest

from src.product.clustering.catalog import ClusterCatalog, ProductCluster


def test_new_version_does_not_overwrite_history():
    catalog = ClusterCatalog()
    catalog.add_version(ProductCluster(cluster_id=17, cluster_version="RP68_2025", cqs=0.780))
    catalog.add_version(ProductCluster(cluster_id=17, cluster_version="RP68_2026", cqs=0.800))

    assert catalog.current(17).cluster_version == "RP68_2026"
    versions = {c.cluster_version for c in catalog.history(17)}
    assert versions == {"RP68_2025", "RP68_2026"}


def test_duplicate_version_rejected():
    catalog = ClusterCatalog()
    catalog.add_version(ProductCluster(cluster_id=17, cluster_version="RP68_2025", cqs=0.780))
    with pytest.raises(ValueError):
        catalog.add_version(ProductCluster(cluster_id=17, cluster_version="RP68_2025", cqs=0.999))


def test_unknown_cluster_current_is_none():
    catalog = ClusterCatalog()
    assert catalog.current(999) is None
