"""Jede Zahl aus der README und aus den Texten der App, nachgerechnet (DEMO-PLAYBOOK §4). Die Zahlen sind exakt oder Bänder; Zeiten kommen nicht vor."""

import math
from pathlib import Path

import pytest

import asy_algorithm as A
import asy_constants as C
import asy_evaluation as ev

S = ev.Settings
README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")


def test_readme_hand_instance_catalan_10():
    assert A.catalan(10)[10] == 16796
    assert 4 ** 10 / (math.sqrt(math.pi) * 10 ** 1.5) == pytest.approx(18707.9, abs=0.05)
    assert 18707.9 / 16796 == pytest.approx(1.1138, abs=1e-4)


def test_readme_hand_instance_system_and_richardson():
    rho, tau, gamma = A.amplitude([(1, 1, 2)])
    assert (round(rho, 6), round(tau, 6), round(gamma, 6)) == (0.25, 2.0, 2.0)
    assert A.fibonacci_pole(2, 5) == [1, 2, 5, 10, 20, 38]
    cat = A.catalan(6)
    assert float(A.richardson(cat, 3)) == pytest.approx(3.6)


def test_readme_standard_case_catalan_100():
    a = S("Catalan", 100, 1)
    a = ev.analyse(a)
    assert A.digit_count(a.seq[100]) == 57 and ev.big_text(a.seq[100]) == "8,96·10⁵⁶ (57 Stellen)"
    assert round(100 * a.error, 4) == 1.1263 and round(100 * a.corrected_error, 5) == -0.01134
    assert round(a.quotient, 4) == 3.9412 and round(a.richardson, 4) == 3.9989
    assert round(a.alpha_hat, 4) == -1.4706


def test_readme_error_table_catalan():
    a = ev.analyse(S("Catalan", 1000, 1))
    assert [r["n"] for r in a.rows] == [10, 20, 50, 100, 200, 500, 1000]
    assert [round(100 * r["Fehler"], 3) for r in a.rows] == [11.383, 5.658, 2.255, 1.126, 0.563, 0.225, 0.113]
    assert [round(r["skaliert"], 4) for r in a.rows] == [1.1383, 1.1316, 1.1277, 1.1263, 1.1257, 1.1253, 1.1251]
    assert [round(100 * r["Fehler mit Korrektur"], 3) for r in a.rows][:4] == [-1.148, -0.285, -0.045, -0.011]


def test_readme_correction_constants_as_measured():
    values = {"Catalan": (1000, 1.1251), "Motzkin": (1000, None), "Zentraler Binomialkoeffizient": (1000, 0.125), "Beschriftete Wurzelbäume": (1000, 0.0833)}
    for family, (n, expected) in values.items():
        a = ev.analyse(S(family, n, 1))
        if expected is not None:
            assert round(a.rows[-1]["skaliert"], 4) == expected, family
    motzkin = ev.analyse(S("Motzkin", 200, 1))
    assert round(motzkin.rows[-1]["skaliert"], 4) == 2.4412 and round(100 * motzkin.error, 4) == 1.2206


def test_readme_double_pole_and_trees():
    pole = ev.analyse(S("Fibonacci-Pole", 300, 2))
    assert round(100 * pole.error, 4) == -0.5149 and round(pole.alpha_hat, 4) == 0.9949
    trees = ev.analyse(S("Wurzelbäume ohne Reihenfolge", 600, 1))
    assert round(trees.richardson, 4) == 2.9558 and round(trees.alpha_hat, 4) == -1.4941
    trees400 = ev.analyse(S("Wurzelbäume ohne Reihenfolge", 400, 1))
    assert round(trees400.richardson, 6) == 2.955733 and round(100 * trees400.error, 4) == -0.8387
    assert A.digit_count(A.catalan(1000)[1000]) == 598 and A.digit_count(A.bell(1000)[1000]) == 1928


def test_readme_bell_and_partitions():
    bell = ev.analyse(S("Bell-Zahlen", 500, 1))
    assert round(bell.quotient, 2) == 107.07 and round(bell.quotient / (500 / math.log(500)), 2) == 1.33
    part = ev.analyse(S("Partitionen", 1000, 1))
    assert round(part.quotient, 4) == 1.0403 and round(100 * part.error, 2) == 1.42 and round(part.error * math.sqrt(1000), 3) == 0.448
    assert math.exp(A.hardy_ramanujan_log(10)) == pytest.approx(48.06, abs=0.05) and A.partitions(10)[10] == 42


def test_readme_transfer_experiment():
    rows = ev.transfer_rows()
    last = {r["a"]: r["n·Fehler"] for r in rows if r["n"] == 1000}
    assert {a: round(v, 3) for a, v in last.items()} == {0.5: -0.125, -0.5: 0.375, 1.5: 0.375, 2.0: 1.0, 3.0: 3.002}
    assert max(abs(r["n·Fehler"] - r["a(a−1)/2"]) for r in rows if r["n"] == 1000) < 0.0021


def test_readme_quotient_experiment():
    res = ev.quotient_rows()
    cat = [r for r in res["rows"] if r["Folge"].startswith("Catalan")]
    assert [round(r["einfacher Quotient"], 4) for r in cat] == [0.1154, 0.0588, 0.0297, 0.0149]
    assert [float(f"{r['Richardson']:.2e}") for r in cat] == [4.35e-3, 1.14e-3, 2.93e-4, 7.41e-5]
    assert round(res["tree_ref"], 4) == 2.9558


def test_readme_spec_experiment():
    res = ev.spec_experiment()
    assert len(res["specs"]) == 24 and C.SPEC_SEED == 20261101
    assert [round(100 * r["mittlerer Fehler"], 2) for r in res["rows"]] == [2.25, 1.12, 0.56]
    assert [round(100 * r["größter Fehler"], 2) for r in res["rows"]][-1] == 2.17
    assert round(sum(res["plain"]) / 24, 4) == 0.0074 and round(1.5 / 200, 4) == 0.0075


def test_readme_classes_and_wrong_exponent():
    rows = {r["Folge"]: r for r in ev.class_rows()}
    assert [round(rows["Catalan (Wurzelsingularität)"][f"n = {n}"], 3) for n in C.CLASS_NS] == [3.5, 3.941, 3.994]
    assert [round(rows["Bell-Zahlen (ganze Funktion)"][f"n = {n}"], 1) for n in C.CLASS_NS] == [5.9, 29.6, 190.6]
    assert [round(rows["Partitionen (wesentliche Singularität)"][f"n = {n}"], 3) for n in C.CLASS_NS] == [1.333, 1.125, 1.040]
    assert [round(rows["n! (Fakultät)"][f"n = {n}"], 1) for n in C.CLASS_NS] == [11.0, 101.0, 1001.0]
    wrong = {r["Exponent"]: round(r["Vorhersage / exakt"], 3) for r in ev.wrong_exponent_rows()}
    assert wrong == {-1.5: 0.99, -0.5: 9.9, -2.5: 0.099, 0.0: 31.306}


def test_readme_play_equations():
    res = ev.play_equation(0, 1, 0, 200)
    assert round(100 * res["error"], 3) == 0.563 and round(res["quotient"], 5) == 3.97030 and round(res["richardson"], 5) == 3.99971
    for c, expected in (((1, 1, 1), (0.154701, 2.366025, 2.897777)), ((2, 0, 3), (0.183013, 3.154701, 5.603214))):
        rho, tau, gamma = A.amplitude(A.spec_terms(*c))
        assert (round(rho, 6), round(tau, 6), round(gamma, 6)) == expected, c
    assert ev.play_equation(0, 0, 1, 200)["kind"] == "periodic"


def test_preset_help_claims():
    cat = ev.analyse(S("Catalan", 100, 1))
    assert round(100 * cat.error, 1) == 1.1 and round(100 * cat.corrected_error, 3) == -0.011
    assert "bei 0,011 %" in C.PRESET_HELP["Standardfall: Catalan, n = 100"]
    mot = ev.analyse(S("Motzkin", 200, 1))
    assert round(mot.rows[-1]["skaliert"], 2) == 2.44
    binom = ev.analyse(S("Zentraler Binomialkoeffizient", 500, 1))
    assert round(binom.rows[-1]["skaliert"], 3) == 0.125
    labelled = ev.analyse(S("Beschriftete Wurzelbäume", 1000, 1))
    assert round(labelled.rows[-1]["skaliert"], 4) == 0.0833
    pole = ev.analyse(S("Fibonacci-Pole", 300, 2))
    assert round(pole.alpha_hat, 1) == 1.0
    part = ev.analyse(S("Partitionen", 1000, 1))
    assert round(100 * part.error, 1) == 1.4


def test_readme_states_the_test_count_and_ends_with_the_footer():
    assert "Stück 9 von 16" in README and "Asymptotik" in README
    assert README.rstrip().endswith("[Interaktive Demos](https://sebastianhanisch.net/demos.html).")
