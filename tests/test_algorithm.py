"""Einheiten des Rechenkerns, jede an einer von Hand gerechneten Mini-Instanz."""

import math
from fractions import Fraction

import pytest

import asy_algorithm as A


def test_digit_count_boundaries():
    assert [A.digit_count(x) for x in (0, 1, 9, 10, 99, 100, 10 ** 50 - 1, 10 ** 50)] == [1, 1, 1, 2, 2, 3, 50, 51]
    with pytest.raises(ValueError):
        A.digit_count(-1)


def test_ln_of_huge_integers_and_fractions():
    assert A.ln(10 ** 5000) == pytest.approx(5000 * math.log(10), rel=1e-12)
    assert A.ln(Fraction(1, 2)) == pytest.approx(-math.log(2))
    with pytest.raises(ValueError):
        A.ln(0)


def test_catalan_hand(hand_catalan):
    assert A.catalan(10) == hand_catalan["seq"]
    assert 4 ** 10 / (math.sqrt(math.pi) * 10 ** 1.5) == pytest.approx(hand_catalan["c10_lead"], abs=0.1)


def test_central_binomial_and_motzkin_hand():
    assert A.central_binomial(5) == [1, 2, 6, 20, 70, 252]
    assert A.motzkin(8) == [1, 1, 2, 4, 9, 21, 51, 127, 323]


def test_fibonacci_pole_hand(hand_fib_square):
    assert A.fibonacci_pole(1, 8) == [1, 1, 2, 3, 5, 8, 13, 21, 34]
    assert A.fibonacci_pole(2, 5) == hand_fib_square


def test_unlabelled_trees_hand():
    assert A.unlabelled_trees(10)[1:] == [1, 1, 2, 4, 9, 20, 48, 115, 286, 719]


def test_labelled_trees_and_bell_hand():
    assert A.labelled_trees(4) == [0, 1, Fraction(2, 2), Fraction(9, 6), Fraction(64, 24)]
    assert A.bell(8) == [1, 1, 2, 5, 15, 52, 203, 877, 4140]


def test_partitions_hand():
    assert A.partitions(10) == [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42]


def test_spec_terms_drop_zero_coefficients():
    assert A.spec_terms(0, 1, 0) == [(1, 1, 2)]
    assert A.spec_terms(0, 0, 0) == []
    assert A.spec_terms(2, 0, 3) == [(2, 1, 1), (3, 2, 2)]


def test_spec_coefficients_catalan_and_validation():
    assert A.spec_coefficients([(1, 1, 2)], 10) == A.catalan(10)
    with pytest.raises(ValueError):
        A.spec_coefficients([(1, 0, 2)], 5)
    with pytest.raises(ValueError):
        A.spec_coefficients([(1, 1, 4)], 5)
    with pytest.raises(ValueError):
        A.spec_coefficients([(-1, 1, 2)], 5)


def test_system_catalan(hand_system_catalan):
    rho, tau, gamma = A.amplitude(hand_system_catalan["terms"])
    assert (rho, tau, gamma) == pytest.approx((hand_system_catalan["rho"], hand_system_catalan["tau"], hand_system_catalan["gamma"]), abs=1e-9)


def test_system_rejects_linear_and_reports_periodic():
    with pytest.raises(ValueError):
        A.solve_system([(1, 1, 1)])
    assert A.is_periodic([(1, 2, 2)]) and not A.is_periodic([(1, 1, 2), (1, 2, 2)]) and not A.is_periodic([])
    assert A.is_nonlinear([(1, 1, 2)]) and not A.is_nonlinear([(3, 1, 1)])


def test_binomial_and_transfer_hand():
    # (1 − z)^(−2) = 1 + 2z + 3z² + …, (1 − z)^(−1/2): 1, 1/2, 3/8
    assert [A.binomial_coefficient(2, n) for n in range(4)] == pytest.approx([1, 2, 3, 4])
    assert [A.binomial_coefficient(0.5, n) for n in range(3)] == pytest.approx([1, 0.5, 0.375])
    assert A.transfer_lead(2, 10) == pytest.approx(10.0)            # n^1/Γ(2)
    assert A.transfer_lead(0.5, 4) == pytest.approx(0.5 ** 0 * 4 ** -0.5 / math.sqrt(math.pi))
    assert A.transfer_error(1, 50) == pytest.approx(0, abs=1e-12)    # geometrische Reihe: exakt
    assert A.transfer_error(2, 10) == pytest.approx(11 / 10 - 1)     # (n+1)/n − 1


def test_ratio_and_richardson_hand(hand_richardson):
    cat = A.catalan(6)
    n = hand_richardson["n"]
    assert float(A.ratio(cat, n)) == pytest.approx(hand_richardson["r_n"]) and float(A.ratio(cat, n + 1)) == pytest.approx(hand_richardson["r_n1"])
    assert float(A.richardson(cat, n)) == pytest.approx(hand_richardson["mu"])


def test_exponent_estimate_hand():
    # Catalan n = 100: r = 3,94117647..., α̂ = 100·(r/4 − 1) = −1,4705882
    cat = A.catalan(102)
    assert A.exponent_estimate(cat, 100, 4) == pytest.approx(-1.4705882352941, abs=1e-9)


def test_predict_with_exponent_is_exact_when_fit_equals_target():
    cat = A.catalan(60)
    assert A.predict_with_exponent(cat, 50, 4.0, -1.5, 50) == pytest.approx(math.exp(A.ln(cat[50]) - A.ln(cat[50])) * 1.0)
    # mit dem richtigen Exponent bleibt die Vorhersage nahe 1
    assert abs(A.predict_with_exponent(cat, 30, 4.0, -1.5, 60) - 1) < 0.02


def test_hardy_ramanujan_hand():
    # n = 10: exp(π·√(20/3)) / (40·√3) = exp(8,1103) / 69,28 ≈ 3329,5 / 69,28 ≈ 48,06 gegen p(10) = 42
    assert math.exp(A.hardy_ramanujan_log(10)) == pytest.approx(48.1, abs=0.2)
