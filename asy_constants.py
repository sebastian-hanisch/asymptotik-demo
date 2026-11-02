"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

FAMILIES = ("Catalan", "Motzkin", "Zentraler Binomialkoeffizient", "Fibonacci-Pole", "Wurzelbäume ohne Reihenfolge", "Beschriftete Wurzelbäume", "Bell-Zahlen", "Partitionen")
DEFAULT_FAMILY = "Catalan"
N_MIN, N_MAX, DEFAULT_N = 10, 1000, 100
N_CAP = {"Catalan": 1000, "Motzkin": 1000, "Zentraler Binomialkoeffizient": 1000, "Fibonacci-Pole": 1000, "Wurzelbäume ohne Reihenfolge": 600,
         "Beschriftete Wurzelbäume": 1000, "Bell-Zahlen": 1000, "Partitionen": 1000}   # größtes n je Familie, das die App rechnet
M_MIN, M_MAX, DEFAULT_M = 1, 3, 1                # Fibonacci-Pole: Vielfachheit des Pols
ERROR_GRID = (10, 20, 50, 100, 200, 500, 1000)   # Stützstellen der Fehlerkurve

ENUM_TREE_N = 10                                 # Wurzelbäume ohne Reihenfolge durch Aufzählen bis hier
EGF_CHECK_N = 150                                # beschriftete Bäume und Bell über den Kalkül aus Stück 6 bis hier
SUBSTITUTION_N = 30                              # eigene Gleichung durch wiederholtes Einsetzen bis hier

TRANSFER_AS = (0.5, -0.5, 1.5, 2.0, 3.0)         # Experiment 2
TRANSFER_NS = (10, 100, 1000)
QUOTIENT_NS = (50, 100, 200, 400)                # Experiment 3
QUOTIENT_TREE_REF = 598                          # Bezugsgröße für die Wachstumskonstante der Wurzelbäume ohne Reihenfolge
SPEC_COUNT, SPEC_SEED = 24, 20261101             # Experiment 4: Zufallsspezifikationen
SPEC_NS = (50, 100, 200)
CLASS_NS = (10, 100, 1000)                       # Experiment 5
WRONG_ALPHAS = (-1.5, -0.5, -2.5, 0.0)
WRONG_FIT_N, WRONG_TARGET_N = 100, 1000
PLAY_N_MIN, PLAY_N_MAX, PLAY_N_DEFAULT = 20, 400, 200   # Spielwiese: eigene Gleichung
PLAY_C_MAX = 3

COLOR_MAIN = "#2F6B65"
COLOR_ALL = "rgba(150,150,150,0.75)"
COLOR_WARN = "#c0504d"
COLOR_LINE = "#4c78a8"

PRESETS = {
    "Standardfall: Catalan, n = 100": {"family": "Catalan", "n": 100, "m": 1},
    "Motzkin-Zahlen, n = 200": {"family": "Motzkin", "n": 200, "m": 1},
    "Zentraler Binomialkoeffizient, n = 500": {"family": "Zentraler Binomialkoeffizient", "n": 500, "m": 1},
    "Doppelter Pol: 1/(1 − z − z²)², n = 300": {"family": "Fibonacci-Pole", "n": 300, "m": 2},
    "Wurzelbäume ohne Reihenfolge, n = 400": {"family": "Wurzelbäume ohne Reihenfolge", "n": 400, "m": 1},
    "Beschriftete Wurzelbäume, n = 1000": {"family": "Beschriftete Wurzelbäume", "n": 1000, "m": 1},
    "Bell-Zahlen: keine Rate, n = 500": {"family": "Bell-Zahlen", "n": 500, "m": 1},
    "Partitionen: Hardy–Ramanujan, n = 1000": {"family": "Partitionen", "n": 1000, "m": 1},
}
PRESET_HELP = {
    "Standardfall: Catalan, n = 100": "Die Catalan-Zahl C₁₀₀ gegen 4ⁿ/(√π·n^(3/2)): der Fehler ist 9/(8n) = 1,1 %; mit dem Korrekturfaktor (1 − 9/(8n)) bleibt er bei 0,011 %.",
    "Motzkin-Zahlen, n = 200": "Gleichung M = 1 + z·M + z²·M²: ρ = 1/3, τ = 3, Amplitude 3√3/(2√π); der Fehler des führenden Terms ist etwa 2,44/n.",
    "Zentraler Binomialkoeffizient, n = 500": "C(2n, n) ~ 4ⁿ/√(πn): die Singularität steht im Nenner (Exponent −1/2 statt −3/2); Fehler 1/(8n).",
    "Doppelter Pol: 1/(1 − z − z²)², n = 300": "Zwei gleiche Pole: c(n) wächst wie n·φⁿ; der Exponent n(r/φ − 1) strebt gegen 1.",
    "Wurzelbäume ohne Reihenfolge, n = 400": "Keine algebraische Gleichung: Wachstumskonstante und Konstante der Näherung werden aus den Zahlen geschätzt (Richardson), der Exponent −3/2 aus der Theorie.",
    "Beschriftete Wurzelbäume, n = 1000": "nⁿ⁻¹/n! gegen eⁿ/(√(2π)·n^(3/2)) (Stirling): Fehler 1/(12n).",
    "Bell-Zahlen: keine Rate, n = 500": "Die Quotienten B(n+1)/B(n) wachsen ohne Grenze: es gibt keine Wachstumsrate und keine Singularität im Endlichen.",
    "Partitionen: Hardy–Ramanujan, n = 1000": "Der Quotient strebt gegen 1 (subexponentiell); der führende Term exp(π√(2n/3))/(4n√3) liegt 1,4 % zu hoch.",
}
