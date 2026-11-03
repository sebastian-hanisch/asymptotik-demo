"""Eigenschaftstests (Schicht 2): Aussagen, die für ganze Klassen von Eingaben gelten, nicht nur für Einzelwerte."""

import math
import random

import pytest

import asy_algorithm as A
import asy_constants as C
import asy_evaluation as ev

ALGEBRAIC = ("Catalan", "Motzkin", "Zentraler Binomialkoeffizient", "Beschriftete Wurzelbäume")


def test_error_of_the_leading_term_decays_like_one_over_n_for_every_algebraic_family():
    for family in ALGEBRAIC:
        a = ev.analyse(ev.Settings(family, 1000, 1))
        rows = [r for r in a.rows if r["n"] >= 100]
        assert len(rows) >= 3
        scaled = [r["skaliert"] for r in rows]
        assert max(scaled) - min(scaled) < 0.02 * abs(scaled[-1]) + 0.01, family            # n·Fehler ist nahezu konstant
        assert all(r["Fehler"] > 0 for r in rows), family                                      # die Näherung liegt immer zu hoch


def test_scaled_error_equals_minus_the_correction_constant():
    expected = {"Catalan": 9 / 8, "Motzkin": 39 / 16, "Zentraler Binomialkoeffizient": 1 / 8, "Beschriftete Wurzelbäume": 1 / 12}
    for family, value in expected.items():
        a = ev.analyse(ev.Settings(family, 1000, 1))
        assert a.rows[-1]["skaliert"] == pytest.approx(value, rel=0.01), family


def test_correction_makes_the_error_smaller_by_at_least_a_factor_of_fifty():
    for family in ALGEBRAIC:
        a = ev.analyse(ev.Settings(family, 200, 1))
        assert abs(a.corrected_error) * 50 < abs(a.error), family


def test_richardson_beats_plain_quotient_for_all_families_with_a_known_rate():
    for family in ALGEBRAIC + ("Fibonacci-Pole",):
        a = ev.analyse(ev.Settings(family, 200, 2 if family == "Fibonacci-Pole" else 1))
        assert abs(a.richardson - a.mu_known) * 5 < abs(a.quotient - a.mu_known), family


def test_fibonacci_pole_exponent_is_m_minus_one():
    for m in (1, 2, 3):
        a = ev.analyse(ev.Settings("Fibonacci-Pole", 500, m))
        assert a.info.alpha == m - 1
        assert a.alpha_hat == pytest.approx(m - 1, abs=0.1)
        assert abs(a.error) < 0.02 * m


def test_transfer_error_tends_to_a_times_a_minus_one_over_two():
    rng = random.Random(7)
    for _ in range(20):
        a = rng.uniform(-0.9, 4.0)
        n = 2000
        assert n * A.transfer_error(a, n) == pytest.approx(a * (a - 1) / 2, abs=0.01 + 0.002 * abs(a) ** 3)


def test_transfer_exponent_rule_root_versus_pole():
    """(1 − z)^(−a): der Koeffizient wächst wie n^(a−1); a = 1/2 − 1 (Wurzelfall) fällt, a = m wächst."""
    for a in (0.5, 1.5, 2.5):
        assert A.binomial_coefficient(a, 2000) / A.binomial_coefficient(a, 1000) == pytest.approx(2 ** (a - 1), rel=1e-2)


def test_random_equations_have_a_valid_singularity():
    rng = random.Random(ev.C.SPEC_SEED)
    for _ in range(40):
        terms = ev.random_spec(rng)
        rho, tau, gamma = A.amplitude(terms)
        assert 0 < rho < 1 and tau > 1 and gamma > 0
        assert A.phi(terms, rho, tau) == pytest.approx(tau, rel=1e-9) and A.phi_y(terms, rho, tau) == pytest.approx(1, rel=1e-9)
        f = A.spec_coefficients(terms, 120)
        assert float(A.richardson(f, 100)) * rho == pytest.approx(1, abs=2e-3)


def test_leading_term_over_exact_is_above_one_for_random_equations():
    rng = random.Random(3)
    for _ in range(25):
        terms = ev.random_spec(rng)
        rho, tau, gamma = A.amplitude(terms)
        f = A.spec_coefficients(terms, 150)
        lead = math.log(gamma / (2 * math.sqrt(math.pi))) - 150 * math.log(rho) - 1.5 * math.log(150)
        assert 0 < math.exp(lead - A.ln(f[150])) - 1 < 0.1


def test_coefficients_grow_monotonically_for_nonnegative_equations():
    for c in [(0, 1, 0), (1, 1, 1), (2, 0, 3), (3, 3, 3)]:
        f = A.spec_coefficients(A.spec_terms(*c), 60)
        assert all(f[i + 1] >= f[i] for i in range(60)), c


def test_all_families_agree_between_their_ways_at_every_grid_size():
    for family in C.FAMILIES:
        for n in (C.N_MIN, 30, 150, 300):
            a = ev.analyse(ev.Settings(family, n, 2))
            assert a.problems == [], (family, n)
            assert all(r["Prüfung"] in ("gleich", "") or r["Ergebnis"] == "–" for r in ev.way_rows(a)), (family, n)


def test_quotient_classes_order():
    rows = {r["Folge"]: r for r in ev.class_rows()}
    bell = rows["Bell-Zahlen (exponentielle Reihe ganz)"]
    part = rows["Partitionen (wesentliche Singularität)"]
    assert bell["n = 10"] < bell["n = 100"] < bell["n = 1000"]
    assert part["n = 10"] > part["n = 100"] > part["n = 1000"] > 1
