from src.product.sales.cluster_performance import classify_trend


def test_growth_classified():
    assert classify_trend(120, 100) == "GROWTH"


def test_decline_classified():
    assert classify_trend(80, 100) == "DECLINE"


def test_stable_classified():
    assert classify_trend(101, 100) == "STABLE"


def test_missing_data_is_unknown():
    assert classify_trend(None, 100) == "UNKNOWN"
    assert classify_trend(100, None) == "UNKNOWN"


def test_zero_previous_baseline_is_unknown_not_division_error():
    assert classify_trend(100, 0) == "UNKNOWN"
