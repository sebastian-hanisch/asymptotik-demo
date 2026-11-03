"""Urteilstexte (Schicht 3): die Texte, die die App zeigt, mit genauem Wortlaut für die Standardfälle, damit jede Zahl darin geprüft ist."""

import asy_evaluation as ev

S = ev.Settings


def test_answer_catalan_standard_case_exact():
    kind, text = ev.verdict_answers(ev.analyse(S("Catalan", 100, 1)))
    assert kind == "success"
    assert text == ("Catalan (Wurzelsingularität): ρ = 0,250000, Wachstumsrate 1/ρ = 4,000000, Exponent −1,5. Der führende Term liegt bei n = 100 1,1263 % neben dem exakten Wert, "
                    "mit Korrekturfaktor (1 + B/n), B = −1,1250, nur noch −0,01134 %. Der einfache Quotient hat den Fehler 0,06, die Richardson-Schätzung 1,1·10⁻³.")


def test_answer_motzkin_and_binomial_numbers():
    text = ev.verdict_answers(ev.analyse(S("Motzkin", 200, 1)))[1]
    assert "1,2206 %" in text and "B = −2,4375" in text and "−0,01304 %" in text and "Wachstumsrate 1/ρ = 3,000000" in text
    text = ev.verdict_answers(ev.analyse(S("Zentraler Binomialkoeffizient", 500, 1)))[1]
    assert "0,0250 %" in text and "Exponent −0,5" in text and "B = −0,1250" in text and "nur noch −3,13·10⁻⁶ %" in text and "0,00000" not in text


def test_answer_double_pole_has_no_correction_constant():
    kind, text = ev.verdict_answers(ev.analyse(S("Fibonacci-Pole", 300, 2)))
    assert kind == "success" and "Pol der Vielfachheit 2" in text and "Exponent 1,0" in text and "−0,5149 %" in text and "Korrekturfaktor" not in text


def test_answer_unlabelled_trees_is_fitted_not_computed():
    kind, text = ev.verdict_answers(ev.analyse(S("Wurzelbäume ohne Reihenfolge", 400, 1)))
    assert kind == "success" and "nicht aus einer Gleichung ablesbar" in text
    assert "μ̂ = 2,955733" in text and "−1,4912" in text and "n = 200 angepasstem K" in text and "−0,8387 %" in text


def test_answer_labelled_trees():
    text = ev.verdict_answers(ev.analyse(S("Beschriftete Wurzelbäume", 1000, 1)))[1]
    assert "ρ = 0,367879" in text and "Wachstumsrate 1/ρ = 2,718282" in text and "0,0083 %" in text and "B = −0,0833" in text


def test_answer_bell_and_partitions_are_warnings_without_a_rate():
    kind, text = ev.verdict_answers(ev.analyse(S("Bell-Zahlen", 500, 1)))
    assert kind == "warning" and "keine Wachstumsrate" in text and "107,07" in text and "1,33-fache" in text and "Sattelpunktmethode" in text
    kind, text = ev.verdict_answers(ev.analyse(S("Partitionen", 1000, 1)))
    assert kind == "warning" and "1,0403" in text and "1,42 %" in text and "≈ 0,448" in text and "Kreismethode" in text


def test_transfer_verdict_exact():
    kind, text = ev.verdict_transfer(ev.transfer_rows())
    assert kind == "success"
    assert text == ("Für (1 − z)^(−a) ist der exakte Koeffizient n^(a−1)/Γ(a)·(1 + a(a−1)/(2n) + …): bei n = 1000 weicht n·Fehler höchstens 0,0020 von a(a−1)/2 ab, "
                    "für a = 1 (geometrische Reihe) ist die Näherung exakt.")


def test_quotient_verdict_exact():
    kind, text = ev.verdict_quotient(ev.quotient_rows())
    assert kind == "success"
    assert text == ("Catalan (Rate 4): beim Verdoppeln von n sinkt der Fehler des einfachen Quotienten um den Faktor 1,96 bis 1,99 (Ordnung 1), der Richardson-Schätzung um 3,81 bis 3,95 (Ordnung 2); "
                    "bei n = 400: 0,01 gegen 7,4·10⁻⁵, etwa 202-mal genauer.")


def test_spec_verdict_exact():
    kind, text = ev.verdict_spec(ev.spec_experiment())
    assert kind == "success"
    assert text == ("Bei 24 zufälligen Gleichungen trifft der führende Term γ/(2√π)·ρ⁻ⁿ·n^(−3/2) aus dem System bei n = 200 im Mittel auf 0,56 % (größter Fehler 2,17 %); der Fehler halbiert sich mit n. "
                    "Der einfache Quotient hat bei n = 200 im Mittel den relativen Fehler 0,0074 (≈ 3/(2n) = 0,0075), die Richardson-Schätzung im Mittel 7,3·10⁻⁵.")


def test_class_verdict_exact():
    kind, text = ev.class_verdict(ev.class_rows())
    assert kind == "warning"
    assert text.startswith("Der Quotient c(n+1)/c(n) verrät die Klasse: Catalan strebt gegen 4 (3,50, 3,941, 3,994)")
    assert "(5,9, 29,6, 190,6)" in text and "(1,333, 1,125, 1,040)" in text and text.endswith("Eine Wachstumsrate gibt es nur im ersten Fall.")


def test_wrong_exponent_verdict_exact():
    kind, text = ev.verdict_wrong(ev.wrong_exponent_rows())
    assert kind == "warning"
    assert text == ("Catalan, Konstante bei n = 100 angepasst, Vorhersage für n = 1000: mit dem richtigen Exponent −1,5 liegt sie um 1,0 % daneben, mit −0,5 um den Faktor 9,9, mit 0 um den Faktor 31,3, "
                    "mit −2,5 um den Faktor 0,099: der Exponent entscheidet.")


def test_play_verdicts_exact():
    kind, text = ev.verdict_play(ev.play_equation(0, 1, 0, 200))
    assert kind == "success"
    assert text == ("F = 1 + z·F²: ρ = 0,250000, τ = 2,000000, γ = 2,000000; c(n) ≈ γ/(2√π)·ρ⁻ⁿ·n^(−3/2) mit Amplitude 0,564190. Bei n = 200 liegt der führende Term 0,563 % neben dem exakten Wert "
                    "(n mal Fehler = 1,126); Quotient 3,97030 gegen 1/ρ = 4,00000, Richardson 3,99971.")
    assert ev.verdict_play(ev.play_equation(0, 0, 0, 200))[0] == "info"
    kind, text = ev.verdict_play(ev.play_equation(0, 0, 1, 200))
    assert kind == "warning" and "Periode 2" in text and "mindestens ein Term mit z¹" in text
    kind, text = ev.verdict_play(ev.play_equation(1, 0, 0, 200))
    assert kind == "success" and text.startswith("Die Gleichung ist linear: F = 1/(1 − z), c(n) = 1ⁿ. Pol bei ρ = 1,000000, Exponent 0")


def test_answer_reports_contradicting_ways_as_error():
    a = ev.analyse(S("Catalan", 100, 1))
    a.problems.append("zwei Wege weichen ab")
    kind, text = ev.verdict_answers(a)
    assert kind == "error" and text == "Die Rechenwege widersprechen sich: zwei Wege weichen ab"
