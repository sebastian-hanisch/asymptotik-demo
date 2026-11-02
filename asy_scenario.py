"""Szenario: aus der gewählten Familie das Modell bauen (Folge, Singularität, Exponent, Konstante, zweiter Rechenweg) und die Größe begrenzen."""

import math
from dataclasses import dataclass
from fractions import Fraction

import asy_algorithm as A
import asy_constants as C


@dataclass(frozen=True)
class FamilyInfo:
    name: str
    kind: str                       # Art der Singularität beziehungsweise Wachstumsklasse
    alpha: object                   # Exponent des polynomiellen Faktors (None: keine Rate)
    rho: object                     # Lage der Singularität (None: keine oder unbekannt)
    amp: object                     # Amplitude A mit c(n) ~ A·ρ⁻ⁿ·n^α (None: unbekannt)
    correction: object              # B mit exakt = Näherung·(1 + B/n) (None: nicht bekannt)
    algebraic: bool                 # Konstante aus einer Gleichung ablesbar


def effective_n(family: str, n: int) -> int:
    if family not in C.FAMILIES:
        raise ValueError(f"unbekannte Familie {family!r}")
    return max(C.N_MIN, min(n, C.N_CAP[family], C.N_MAX))


def family_info(family: str, m: int = 1) -> FamilyInfo:
    if family not in C.FAMILIES:
        raise ValueError(f"unbekannte Familie {family!r}")
    if family == "Catalan":
        return FamilyInfo(family, "Wurzelsingularität", -1.5, 0.25, 1 / math.sqrt(math.pi), Fraction(-9, 8), True)
    if family == "Motzkin":
        return FamilyInfo(family, "Wurzelsingularität", -1.5, 1 / 3, 3 * math.sqrt(3) / (2 * math.sqrt(math.pi)), Fraction(-39, 16), True)
    if family == "Zentraler Binomialkoeffizient":
        return FamilyInfo(family, "Wurzelsingularität im Nenner", -0.5, 0.25, 1 / math.sqrt(math.pi), Fraction(-1, 8), True)
    if family == "Fibonacci-Pole":
        m = max(C.M_MIN, min(m, C.M_MAX))
        k2 = 1 + 1 / A.PHI ** 2
        return FamilyInfo(family, "Pol" if m == 1 else f"Pol der Vielfachheit {m}", m - 1, 1 / A.PHI, 1 / (math.gamma(m) * k2 ** m), None, True)
    if family == "Wurzelbäume ohne Reihenfolge":
        return FamilyInfo(family, "Wurzelsingularität (nicht algebraisch)", -1.5, None, None, None, False)
    if family == "Beschriftete Wurzelbäume":
        return FamilyInfo(family, "Wurzelsingularität", -1.5, 1 / math.e, 1 / math.sqrt(2 * math.pi), Fraction(-1, 12), True)
    if family == "Bell-Zahlen":
        return FamilyInfo(family, "keine Rate: ganze Funktion, der Quotient wächst", None, None, None, None, False)
    return FamilyInfo(family, "keine Rate: wesentliche Singularität, der Quotient strebt gegen 1", None, None, None, None, False)


def make_sequence(family: str, m: int, n_max: int) -> list:
    """Die Folge c[0..n_max] der gewählten Familie."""
    if family == "Catalan":
        return A.catalan(n_max)
    if family == "Motzkin":
        return A.motzkin(n_max)
    if family == "Zentraler Binomialkoeffizient":
        return A.central_binomial(n_max)
    if family == "Fibonacci-Pole":
        return A.fibonacci_pole(max(C.M_MIN, min(m, C.M_MAX)), n_max)
    if family == "Wurzelbäume ohne Reihenfolge":
        return A.unlabelled_trees(n_max)
    if family == "Beschriftete Wurzelbäume":
        return A.labelled_trees(n_max)
    if family == "Bell-Zahlen":
        return A.bell(n_max)
    if family == "Partitionen":
        return A.partitions(n_max)
    raise ValueError(f"unbekannte Familie {family!r}")
