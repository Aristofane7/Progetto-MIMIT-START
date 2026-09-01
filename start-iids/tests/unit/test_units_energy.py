"""P0 mandatory tests — spec sec. 7.2, 42, 53 (Stage 0 DoD: "mj_to_gj test passa")."""
from src.core.units.energy import (
    gas_nm3_to_mj,
    gj_to_mj,
    kwh_to_mj,
    mj_to_gj,
)


def test_mj_to_gj():
    assert mj_to_gj(1000) == 1


def test_mj_to_gj_is_not_j_to_gj():
    # The manuals' defective convention (mj / 1e9) must NOT be reproduced.
    assert mj_to_gj(1000) != 1000 / 1e9


def test_mj_to_gj_zero():
    assert mj_to_gj(0) == 0


def test_gj_to_mj_roundtrip():
    original = 4321.5
    assert gj_to_mj(mj_to_gj(original)) == original


def test_kwh_to_mj():
    # spec sec. 14.3 / 15.2: Ex_el[MJ] = kWh * 3.6
    assert kwh_to_mj(1) == 3.6
    assert kwh_to_mj(100) == 360.0


def test_gas_nm3_to_mj():
    # spec sec. 14.3: Ex_gas[MJ] = Nm3 * PCI * f_ex
    assert gas_nm3_to_mj(volume_nm3=10, pci_mj_per_nm3=35.0, exergy_factor=1.04) == 10 * 35.0 * 1.04
