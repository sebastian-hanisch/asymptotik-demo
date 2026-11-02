"""Unabhängige Orakel: jede Folge und jede Konstante über einen zweiten Weg, der den Rechenkern nicht benutzt."""

import math
from fractions import Fraction
from itertools import product

import pytest

import asy_algorithm as A


def test_catalan_by_binomial_formula_and_by_dyck_recursion():
    cat = A.catalan(40)
    assert all(cat[n] == math.comb(2 * n, n) // (n + 1) for n in range(41))
    # Zerlegung C_{n+1} = Σ C_k C_{n−k} (Dyck-Wörter)
    assert all(cat[n + 1] == sum(cat[k] * cat[n - k] for k in range(n + 1)) for n in range(40))


def test_motzkin_by_trinomial_sum():
    """M_n = Σ_k C(n, 2k)·Catalan_k (Wege mit Auf-, Ab- und flachen Schritten: 2k Schritte nach oben/unten, der Rest flach)."""
    assert A.motzkin(40) == [sum(math.comb(n, 2 * k) * (math.comb(2 * k, k) // (k + 1)) for k in range(n // 2 + 1)) for n in range(41)]


def test_fibonacci_poles_by_linear_recurrence():
    """Koeffizient von 1/(1 − z − z²)^m: c_m(n) = c_m(n−1) + c_m(n−2) + c_(m−1)(n) (Multiplikation mit (1 − z − z²) rückwärts)."""
    prev = A.fibonacci_pole(1, 40)
    for m in (2, 3):
        cur = []
        for n in range(41):
            cur.append(prev[n] + (cur[n - 1] if n >= 1 else 0) + (cur[n - 2] if n >= 2 else 0))
        assert cur == A.fibonacci_pole(m, 40) == A.fibonacci_pole_by_division(m, 40)
        prev = cur


def test_unlabelled_trees_by_canonical_enumeration():
    t = A.unlabelled_trees(10)
    assert all(t[n] == A.trees_canonical_count(n) for n in range(1, 11))


def test_labelled_trees_by_cayley_and_bell_by_stirling_sum():
    t = A.labelled_trees(30)
    assert all(t[n] == Fraction(n ** (n - 1), math.factorial(n)) for n in range(1, 31))
    assert A.labelled_trees_counts(12)[1:] == [n ** (n - 1) for n in range(1, 13)]
    stirling = [[1]]
    for n in range(1, 40):
        row = [0] * (n + 1)
        for k in range(1, n + 1):
            row[k] = (stirling[n - 1][k] * k if k < n else 0) + stirling[n - 1][k - 1]
        stirling.append(row)
    stirling_bell = [sum(row) for row in stirling]
    assert A.bell(39) == stirling_bell and A.bell_by_exp(30) == stirling_bell[:31]


def partitions_by_coin_change(n_max):
    ways = [1] + [0] * n_max
    for part in range(1, n_max + 1):
        for total in range(part, n_max + 1):
            ways[total] += ways[total - part]
    return ways


def test_partitions_by_coin_change_and_product():
    assert A.partitions(200) == partitions_by_coin_change(200)
    assert A.partitions_by_product(60) == A.partitions(60)


def test_spec_coefficients_agree_with_substitution_for_all_small_equations():
    for c1, c2, c3 in product(range(0, 4), repeat=3):
        terms = A.spec_terms(c1, c2, c3)
        assert A.spec_coefficients(terms, 12) == A.spec_by_substitution(terms, 12), (c1, c2, c3)


def test_singularity_system_satisfies_both_equations_and_matches_the_growth():
    for c1, c2, c3 in [(0, 1, 0), (1, 1, 1), (2, 0, 3), (1, 2, 1), (3, 1, 0)]:
        terms = A.spec_terms(c1, c2, c3)
        rho, tau = A.solve_system(terms)
        assert A.phi(terms, rho, tau) == pytest.approx(tau, rel=1e-10) and A.phi_y(terms, rho, tau) == pytest.approx(1, rel=1e-10), (c1, c2, c3)
        f = A.spec_coefficients(terms, 402)
        assert float(A.richardson(f, 400)) * rho == pytest.approx(1, abs=1e-3), (c1, c2, c3)   # Wachstumsrate unabhängig aus den Zahlen


def test_amplitude_against_closed_forms():
    rho, tau, gamma = A.amplitude([(1, 1, 2)])
    assert gamma / (2 * math.sqrt(math.pi)) == pytest.approx(1 / math.sqrt(math.pi))
    rho, tau, gamma = A.amplitude([(1, 1, 1), (1, 2, 2)])           # Motzkin
    assert (rho, tau) == pytest.approx((1 / 3, 3.0)) and gamma / (2 * math.sqrt(math.pi)) == pytest.approx(3 * math.sqrt(3) / (2 * math.sqrt(math.pi)))
    rho, tau, gamma = A.amplitude([(1, 1, 1), (1, 1, 2)])           # F = 1 + zF + zF²
    # Φ_y = z(1 + 2y) = 1, y = 1 + z y + z y²: y² z − (1 − z) y + 1... aus der Auflösung: ρ = 3 − 2√2
    assert rho == pytest.approx(3 - 2 * math.sqrt(2), rel=1e-9)


def test_correction_constants_by_exact_extrapolation():
    """B in c(n) = Näherung·(1 + B/n + …): aus exakten Zahlen bei großem n (zwei Genauigkeitsstufen) wiederhergestellt."""
    cases = {"catalan": (A.catalan(2000), lambda n: 4 ** n / (math.sqrt(math.pi) * n ** 1.5), -9 / 8),
             "central": (A.central_binomial(2000), lambda n: 4 ** n / math.sqrt(math.pi * n), -1 / 8)}
    for name, (seq, lead, b) in cases.items():
        n = 2000
        value = float(Fraction(seq[n], 4 ** n)) * math.sqrt(math.pi) * (n ** 1.5 if name == "catalan" else n ** 0.5)
        assert n * (value - 1) == pytest.approx(b, abs=2e-3), name
    trees = A.labelled_trees(1000)
    n = 1000
    ratio = A.ln(trees[n]) - (n - 0.5 * math.log(2 * math.pi) - 1.5 * math.log(n))
    assert n * math.expm1(ratio) == pytest.approx(-1 / 12, abs=1e-3)


def test_richardson_cancels_the_first_order_term():
    cat = A.catalan(404)
    e1 = [abs(float(A.ratio(cat, n)) - 4) for n in (50, 100, 200, 400)]
    e2 = [abs(float(A.richardson(cat, n)) - 4) for n in (50, 100, 200, 400)]
    assert all(1.9 < e1[i] / e1[i + 1] < 2.1 for i in range(3))
    assert all(3.7 < e2[i] / e2[i + 1] < 4.1 for i in range(3))


def test_hardy_ramanujan_error_scales_like_one_over_sqrt_n():
    for n in (100, 1000):
        exact = math.log(partitions_by_coin_change(n)[n])
        assert math.exp(A.hardy_ramanujan_log(n) - exact) - 1 == pytest.approx(0.448 / math.sqrt(n), rel=0.05)
