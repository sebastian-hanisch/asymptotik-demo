"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def hand_catalan():
    """Catalan-Zahlen 1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796 (C_10). Nähe: 4¹⁰/(√π·10^1,5) = 18707,9; Verhältnis 18707,9 / 16796 = 1,1138 (Fehler ≈ 9/(8·10) = 11 %)."""
    return {"seq": [1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796], "c10_lead": 18707.9, "ratio_10": 429 / 132}


@pytest.fixture
def hand_system_catalan():
    """F = 1 + z·F²: Φ_y = 2zF = 1 und F = 1 + zF² geben τ = 2, ρ = 1/4; Φ_z = τ² = 4, Φ_yy = 2ρ·2 = 1 ... genauer 2z = 1/2; γ = √(2·(1/4)·4 / (1/2)) = 2."""
    return {"terms": [(1, 1, 2)], "rho": 0.25, "tau": 2.0, "gamma": 2.0}


@pytest.fixture
def hand_fib_square():
    """1/(1 − z − z²)² = (1 + z + 2z² + 3z³ + 5z⁴ + …)²: 1, 2, 5, 10, 20, 38."""
    return [1, 2, 5, 10, 20, 38]


@pytest.fixture
def hand_richardson():
    """Catalan n = 3: r(3) = 14/5 = 2,8, r(4) = 42/14 = 3; μ̂ = 4·3 − 3·2,8 = 3,6."""
    return {"n": 3, "r_n": 2.8, "r_n1": 3.0, "mu": 3.6}
