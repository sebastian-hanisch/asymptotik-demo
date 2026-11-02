"""Randfälle: Grenzen der Regler, unbekannte Eingaben, Entartungen der eigenen Gleichung, riesige Zahlen, Formatierung."""

import math

import pytest

import asy_algorithm as A
import asy_constants as C
import asy_evaluation as ev
import asy_scenario as S


def test_effective_n_clamps_to_range_and_family_cap():
    assert S.effective_n("Catalan", 3) == C.N_MIN
    assert S.effective_n("Catalan", 5000) == C.N_MAX
    assert S.effective_n("Wurzelbäume ohne Reihenfolge", 1000) == 600
    assert S.effective_n("Wurzelbäume ohne Reihenfolge", 400) == 400
    with pytest.raises(ValueError):
        S.effective_n("Unbekannt", 100)


def test_unknown_family_is_rejected_everywhere():
    with pytest.raises(ValueError):
        S.family_info("Unbekannt")
    with pytest.raises(ValueError):
        S.make_sequence("Unbekannt", 1, 10)


def test_m_is_clamped_for_fibonacci_poles():
    assert S.family_info("Fibonacci-Pole", 7).alpha == C.M_MAX - 1
    assert S.family_info("Fibonacci-Pole", -3).alpha == C.M_MIN - 1
    assert S.make_sequence("Fibonacci-Pole", 9, 6) == A.fibonacci_pole(C.M_MAX, 6)


def test_analyse_at_the_slider_limits_for_every_family_without_problems():
    for family in C.FAMILIES:
        for n in (0, C.N_MIN, C.N_MAX, 10 ** 6):
            a = ev.analyse(ev.Settings(family, n, 1))
            assert a.problems == [] and C.N_MIN <= a.n_eff <= C.N_CAP[family], (family, n)
            assert (len(a.notes) == 1) == (a.n_eff != n)


def test_cap_note_names_the_cap():
    a = ev.analyse(ev.Settings("Wurzelbäume ohne Reihenfolge", 1000, 1))
    assert a.n_eff == 600 and a.notes == ["Für diese Familie rechnet die App höchstens bis n = 600: gerechnet wird mit n = 600."]


def test_huge_numbers_do_not_need_string_conversion():
    a = ev.analyse(ev.Settings("Bell-Zahlen", 1000, 1))
    assert len(a.seq) == 1003 and A.digit_count(a.seq[1000]) > 1900          # über dem Limit von 4300 Stellen liegt die Zahl nicht, aber sie ist lang
    assert ev.big_text(10 ** 5000).endswith("(5001 Stellen)") and ev.big_text(10 ** 5000).startswith("1,00·10")
    assert A.digit_count(10 ** 5000) == 5001


def test_big_text_boundaries():
    assert ev.big_text(0) == "0" and ev.big_text(999999999999) == "999.999.999.999"
    assert ev.big_text(10 ** 12) == "1,00·10¹² (13 Stellen)"
    assert ev.big_text(123456789012345) == "1,23·10¹⁴ (15 Stellen)"


def test_formatting_helpers():
    assert ev.de(-1.5, 1) == "−1,5" and ev.de(0, 2) == "0,00"
    assert ev.sci_text(0) == "0" and ev.sci_text(0.5) == "0,50" and ev.sci_text(-0.5) == "−0,50"
    assert ev.sci_text(1.23e-4, 3) == "1,23·10⁻⁴" and ev.sci_text(25000, 2) == "2,5·10⁴"
    assert ev.percent(0.01126, 3) == "1,126 %" and ev.percent(-0.00011, 3) == "−0,011 %"
    assert ev.ln_text(100 * math.log(10)) == "1,00·10¹⁰⁰"
    assert ev.percent_fine(-0.0001134, 5) == "−0,01134 %" and ev.percent_fine(-3.13e-10, 5) == "−3,13·10⁻⁸ %" and "0,00000" not in ev.percent_fine(1e-12)


def test_play_equation_clamps_inputs():
    res = ev.play_equation(99, -5, 0, 10 ** 6)
    assert res["n"] == C.PLAY_N_MAX and res["terms"] == [(C.PLAY_C_MAX, 1, 1)] and res["kind"] == "pole"
    assert ev.play_equation(0, 1, 0, 0)["n"] == C.PLAY_N_MIN


def test_play_equation_degenerate_kinds():
    assert ev.play_equation(0, 0, 0, 100)["kind"] == "trivial"
    assert ev.play_equation(0, 0, 1, 100)["kind"] == "periodic"
    assert ev.play_equation(0, 0, 3, 100)["kind"] == "periodic"
    pole = ev.play_equation(2, 0, 0, 100)
    assert pole["kind"] == "pole" and pole["seq"][10] == 2 ** 10 and pole["error"] == pytest.approx(0, abs=1e-12) and pole["mu"] == 2


def test_play_equation_linear_text_has_no_coefficient_one():
    text = ev.verdict_play(ev.play_equation(1, 0, 0, 100))[1]
    assert "1/(1 − z)" in text and "1z" not in text
    assert "1/(1 − 3z)" in ev.verdict_play(ev.play_equation(3, 0, 0, 100))[1]


def test_play_equation_all_combinations_never_raise():
    for c1 in range(4):
        for c2 in range(4):
            for c3 in range(4):
                res = ev.play_equation(c1, c2, c3, 60)
                kind, text = ev.verdict_play(res)
                assert kind in ("success", "warning", "info") and text, (c1, c2, c3)


def test_play_equation_text_formats_coefficients():
    assert ev.equation_text(0, 1, 0) == "F = 1 + z·F²"
    assert ev.equation_text(2, 0, 3) == "F = 1 + 2z·F + 3z²·F²"
    assert ev.equation_text(0, 0, 0) == "F = 1"


def test_solve_system_when_terms_are_missing_or_linear():
    with pytest.raises(ValueError):
        A.solve_system([])
    with pytest.raises(ValueError):
        A.solve_system([(2, 3, 1)])


def test_ratio_of_zero_coefficient_is_an_error_for_periodic_input():
    f = A.spec_coefficients([(1, 2, 2)], 10)
    assert f[1] == 0
    with pytest.raises(ZeroDivisionError):
        A.ratio(f, 1)


def test_wrong_exponent_rows_follow_the_exponent_order():
    rows = {r["Exponent"]: r["Vorhersage / exakt"] for r in ev.wrong_exponent_rows()}
    assert rows[-2.5] < rows[-1.5] < rows[-0.5] < rows[0.0]
