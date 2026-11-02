"""Oberfläche: jede Familie, jedes Preset, Permalink mit Müll, die Spielwiese und das PDF laufen ohne Ausnahme und zeigen die erwarteten Texte."""

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import asy_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _run(query=None, **state):
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (query or {}).items():
        at.query_params[key] = value
    at.run()
    for key, value in state.items():
        at.session_state[key] = value
    if state:
        at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texts(at):
    return [e.value for e in at.success] + [e.value for e in at.warning] + [e.value for e in at.info] + [e.value for e in at.error]


def test_standard_case_shows_all_five_experiments_and_the_catalan_answer():
    at = _run()
    heads = [s.value for s in at.subheader]
    assert [h for h in heads if h.startswith("🔬 Experiment")] == ["🔬 Experiment 1: Dieselben Zahlen auf allen Wegen", "🔬 Experiment 2: Der Transfersatz", "🔬 Experiment 3: Quotient gegen Richardson",
                                                                   "🔬 Experiment 4: Von der Gleichung zur Konstanten", "🔬 Experiment 5: Wachstumsklassen und falscher Exponent"]
    texts = _texts(at)
    assert any(t.startswith("Catalan (Wurzelsingularität): ρ = 0,250000") for t in texts)
    assert "Alle gerechneten Wege geben dieselbe Zahl." in texts
    assert not at.error


def test_metrics_of_the_standard_case():
    at = _run()
    values = {m.label: m.value for m in at.metric}
    assert values["c(100) exakt"] == "8,96·10⁵⁶ (57 Stellen)" and values["Wachstumsrate 1/ρ"] == "4,000000"
    assert values["Fehler des führenden Terms"] == "1,1263 %" and values["Exponent"] == "−1,5"


def test_every_preset_runs_and_shows_its_family():
    for name, preset in C.PRESETS.items():
        at = _run(family_select=preset["family"], n_slider=preset["n"], m_slider=preset["m"])
        assert at.selectbox(key="family_select").value == preset["family"], name
        assert not at.error, name


def test_bell_and_partitions_show_no_rate():
    for family, word in (("Bell-Zahlen", "keine Wachstumsrate"), ("Partitionen", "keine Wachstumsrate")):
        at = _run(family_select=family, n_slider=300)
        assert any(word in t for t in _texts(at)), family
        assert {m.label: m.value for m in at.metric}["Wachstumsrate 1/ρ"] == "keine"


def test_unlabelled_trees_are_capped_with_a_note():
    at = _run(family_select="Wurzelbäume ohne Reihenfolge", n_slider=1000)
    assert any("höchstens bis n = 600" in t for t in _texts(at))


def test_permalink_garbage_falls_back_to_defaults():
    at = _run(query={"family": "Unsinn", "n": "abc", "m": "99"})
    assert at.selectbox(key="family_select").value == C.DEFAULT_FAMILY and at.slider(key="n_slider").value == C.DEFAULT_N
    assert at.slider(key="m_slider").value == C.M_MAX                              # zu große Zahlen werden auf die Grenze begrenzt


def test_play_ground_all_kinds():
    for (c1, c2, c3), word in (((0, 1, 0), "F = 1 + z·F²"), ((1, 0, 0), "linear"), ((0, 0, 1), "Periode 2"), ((0, 0, 0), "leere Struktur"), ((3, 3, 3), "ρ =")):
        at = _run(play_c1=c1, play_c2=c2, play_c3=c3)
        assert any(word in t for t in _texts(at)), (c1, c2, c3)


def test_pdf_button_makes_a_download():
    at = _run()
    at.button(key="pdf_make").click().run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert any(getattr(b, "key", None) == "pdf_download" or "PDF herunterladen" in str(getattr(b, "label", "")) for b in at.get("download_button"))


def test_charts_have_unique_keys():
    at = _run()
    keys = [c.key for c in at.get("plotly_chart")]
    assert len(keys) == len(set(keys)) and {"main_chart", "transfer_chart", "quotient_chart", "spec_chart", "classes_chart", "play_chart"} <= set(keys)


def test_error_chart_reference_line_follows_the_family():
    import asy_evaluation as ev
    import asy_visualization as V
    for family, name in (("Catalan", "Linie ∝ 1/n"), ("Partitionen", "Linie ∝ 1/√n")):
        a = ev.analyse(ev.Settings(family, 1000, 1))
        fig = V.build_error(a.rows, power=0.5 if family == "Partitionen" else 1.0)
        line = [t for t in fig.data if t.name == name][0]
        ys = list(line.y)
        expected = (a.rows[0]["n"] / a.rows[-1]["n"]) ** (0.5 if family == "Partitionen" else 1.0)
        assert ys[-1] / ys[0] == pytest.approx(expected, rel=1e-9), family
