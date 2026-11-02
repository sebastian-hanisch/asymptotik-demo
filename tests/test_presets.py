"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset zeigt etwas anderes."""

import asy_constants as C
import asy_evaluation as ev
import asy_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds():
    for name, preset in C.PRESETS.items():
        assert preset["family"] in C.FAMILIES and C.N_MIN <= preset["n"] <= C.N_MAX and C.M_MIN <= preset["m"] <= C.M_MAX, name
        assert preset["n"] <= C.N_CAP[preset["family"]], name


def test_default_preset_equals_default_settings_and_comes_first():
    first = next(iter(C.PRESETS.values()))
    assert first == {"family": C.DEFAULT_FAMILY, "n": C.DEFAULT_N, "m": C.DEFAULT_M}
    for field, key in P.PRESET_KEYS.items():
        assert first[field] == P.SETTING_SPECS[key].default


def test_every_preset_passes_the_checker_without_notes():
    for name, preset in C.PRESETS.items():
        a = ev.analyse(ev.Settings(**preset))
        assert a.problems == [] and a.notes == [] and a.n_eff == preset["n"], name


def test_presets_differ_from_each_other_in_the_family_or_the_pole_multiplicity():
    seen = {(p["family"], p["m"] if p["family"] == "Fibonacci-Pole" else 1) for p in C.PRESETS.values()}
    assert len(seen) == len(C.PRESETS)


def test_every_family_has_a_preset():
    assert {p["family"] for p in C.PRESETS.values()} == set(C.FAMILIES)


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    assert P.SETTING_SPECS["family_select"].choices == C.FAMILIES
