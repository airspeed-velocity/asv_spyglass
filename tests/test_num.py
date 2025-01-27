from asv_spyglass._num import Ratio
import math


def test_ratio_normal_calculation():
    ratio = Ratio(t1=10, t2=5)
    assert ratio.val == 0.5
    assert str(ratio) == "  0.50"


def test_ratio_t2_bigger():
    ratio = Ratio(t1=5, t2=10)
    assert ratio.val == 2.0
    assert str(ratio) == "  2.00"


def test_ratio_division_by_zero():
    ratio = Ratio(t1=0, t2=10)
    assert ratio.val == math.inf
    assert str(ratio) == "n/a"


def test_ratio_t1_is_nan():
    ratio = Ratio(t1=float("nan"), t2=10)
    assert ratio.val == math.inf
    assert str(ratio) == "n/a"


def test_ratio_t2_is_nan():
    ratio = Ratio(t1=10, t2=float("nan"))
    assert ratio.val == math.inf
    assert str(ratio) == "n/a"


def test_ratio_both_nan():
    ratio = Ratio(t1=float("nan"), t2=float("nan"))
    assert ratio.val == math.inf
    assert str(ratio) == "n/a"


def test_ratio_t1_none():
    ratio = Ratio(t1=None, t2=10)
    assert ratio.val == math.inf
    assert str(ratio) == "n/a"


def test_ratio_t2_none():
    ratio = Ratio(t1=10, t2=None)
    assert ratio.val == math.inf
    assert str(ratio) == "n/a"


def test_ratio_is_insignificant():
    ratio = Ratio(t1=10, t2=500)
    ratio.is_insignificant = True
    assert ratio.val == 50
    assert str(ratio) == '~50.00'
