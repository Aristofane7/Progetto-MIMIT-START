from src.product.sales.channel_concentration import compute_channel_concentration


def test_even_split_across_two_channels():
    assert compute_channel_concentration({"B2B": 50.0, "B2C": 50.0}) == 0.5


def test_fully_concentrated_in_one_channel():
    assert compute_channel_concentration({"B2B": 100.0, "B2C": 0.0}) == 1.0


def test_uneven_split_matches_hhi_formula():
    # 70/30 split: 0.7^2 + 0.3^2 = 0.49 + 0.09 = 0.58
    result = compute_channel_concentration({"B2B": 70.0, "B2C": 30.0})
    assert abs(result - 0.58) < 1e-9


def test_no_channels_returns_none():
    assert compute_channel_concentration({}) is None


def test_zero_total_sales_returns_none():
    assert compute_channel_concentration({"B2B": 0.0, "B2C": 0.0}) is None


def test_none_values_are_ignored_not_a_type_error():
    assert compute_channel_concentration({"B2B": 100.0, "B2C": None}) == 1.0
