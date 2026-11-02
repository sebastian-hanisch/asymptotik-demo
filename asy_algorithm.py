"""Rechenkern: Asymptotik von Zählfolgen. Exakte Folgen (Catalan, Motzkin, zentraler Binomialkoeffizient, Pole, Wurzelbäume, Bell, Partitionen), das System τ = Φ(ρ, τ), Φ_y(ρ, τ) = 1 mit Amplitude γ,
Transfersatz, Quotientenverfahren und Richardson-Extrapolation.

Folgen sind Listen c[0..n] ganzer Zahlen (bei beschrifteten Bäumen `Fraction`: Koeffizient der exponentiellen erzeugenden Funktion). Logarithmen großer Zahlen über `ln`, damit nichts überläuft."""

import math
from fractions import Fraction

C = math.comb
PHI = (1 + 5 ** 0.5) / 2


# ----------------------------------------------------------------------------- Zahlen

def digit_count(x: int) -> int:
    """Zahl der Dezimalstellen einer ganzen Zahl x >= 0, ohne sie in einen String zu wandeln (Python begrenzt die Umwandlung auf 4300 Stellen)."""
    if x < 0:
        raise ValueError("x darf nicht negativ sein")
    d = max(1, int(x.bit_length() * 0.30102999566398))
    while 10 ** d <= x:
        d += 1
    while d > 1 and 10 ** (d - 1) > x:
        d -= 1
    return d


def ln(x) -> float:
    """Natürlicher Logarithmus einer beliebig großen ganzen oder gebrochenen positiven Zahl."""
    if isinstance(x, Fraction):
        return ln(x.numerator) - ln(x.denominator)
    if x <= 0:
        raise ValueError("Logarithmus verlangt eine positive Zahl")
    return math.log(x)


# ----------------------------------------------------------------------------- Folgen

def catalan(n_max: int) -> list:
    return [C(2 * n, n) // (n + 1) for n in range(n_max + 1)]


def central_binomial(n_max: int) -> list:
    return [C(2 * n, n) for n in range(n_max + 1)]


def motzkin(n_max: int) -> list:
    m = [1, 1][: n_max + 1]
    for n in range(2, n_max + 1):
        m.append(((2 * n + 1) * m[n - 1] + (3 * n - 3) * m[n - 2]) // (n + 2))
    return m


def fibonacci_pole(m: int, n_max: int) -> list:
    """Koeffizienten von 1/(1 − z − z²)^m durch m-fache Faltung der Fibonacci-Folge 1, 1, 2, 3, 5, …"""
    if m < 1:
        raise ValueError("m muss mindestens 1 sein")
    f = [1, 1]
    for _ in range(2, n_max + 1):
        f.append(f[-1] + f[-2])
    f = f[: n_max + 1]
    seq = f
    for _ in range(m - 1):
        seq = [sum(seq[i] * f[n - i] for i in range(n + 1)) for n in range(n_max + 1)]
    return seq


def fibonacci_pole_by_division(m: int, n_max: int) -> list:
    """Dieselben Koeffizienten durch m-faches Teilen durch 1 − z − z²: g_n = f_n + g_(n−1) + g_(n−2)."""
    seq = [1] + [0] * n_max
    for _ in range(m):
        g = []
        for n in range(n_max + 1):
            g.append(seq[n] + (g[n - 1] if n >= 1 else 0) + (g[n - 2] if n >= 2 else 0))
        seq = g
    return seq


def unlabelled_trees(n_max: int) -> list:
    """Wurzelbäume ohne Reihenfolge (Stück 5): t[0] = 0, t[1] = 1, 1, 2, 4, 9, 20, …"""
    t = [0, 1][: n_max + 1]
    c = [1]
    for size in range(1, n_max):
        b = [0] * (size + 1)
        for d in range(1, size + 1):
            for k in range(d, size + 1, d):
                b[k] += d * t[d]
        s = sum(b[k] * c[size - k] for k in range(1, size + 1))
        if s % size:
            raise ArithmeticError("Division geht nicht auf")
        c.append(s // size)
        t.append(c[size])
    return t


def trees_canonical_count(n: int) -> int:
    """Wurzelbäume ohne Reihenfolge durch Aufzählen: alle Bäume mit Reihenfolge erzeugen, Kinder sortieren, gleiche Formen zusammenfassen."""
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def forests(total):
        if total == 0:
            return [()]
        out = []
        for s in range(1, total + 1):
            for tree in forests(s - 1):
                for rest in forests(total - s):
                    out.append((tree,) + rest)
        return out

    def canon(tree):
        return tuple(sorted(canon(c) for c in tree))

    return len({canon(t) for t in forests(n - 1)})


def labelled_trees(n_max: int) -> list:
    """Koeffizienten n^(n−1)/n! der exponentiellen erzeugenden Funktion der beschrifteten Wurzelbäume (als Brüche), Index 0 ist 0."""
    return [Fraction(0)] + [Fraction(n ** (n - 1), math.factorial(n)) for n in range(1, n_max + 1)]


def labelled_trees_counts(n_max: int) -> list:
    """Zahl der beschrifteten Wurzelbäume über die Rekursion T = z·exp(T) (ganze Zahlen, Stück 6): t_n = n·E_(n−1), E = exp(T)."""
    t = [0]
    e = [1]
    for n in range(1, n_max + 1):
        m = n - 1
        if m >= 1:
            e.append(sum(C(m - 1, j - 1) * t[j] * e[m - j] for j in range(1, m + 1)))
        t.append(n * e[m])
    return t


def bell(n_max: int) -> list:
    row, out = [1], [1]
    for _ in range(n_max):
        new = [row[-1]]
        for x in row:
            new.append(new[-1] + x)
        row = new
        out.append(row[0])
    return out


def bell_by_exp(n_max: int) -> list:
    """Bell-Zahlen über exp(e^z − 1) im beschrifteten Kalkül (Stück 6): E_n = Summe C(n−1, k−1)·E_(n−k)."""
    e = [1]
    for n in range(1, n_max + 1):
        e.append(sum(C(n - 1, k - 1) * e[n - k] for k in range(1, n + 1)))
    return e


def partitions(n_max: int) -> list:
    """Zahlpartitionen über Eulers Fünfeckszahlensatz."""
    p = [1] + [0] * n_max
    for n in range(1, n_max + 1):
        s, k = 0, 1
        while k * (3 * k - 1) // 2 <= n:
            sign = 1 if k % 2 else -1
            s += sign * p[n - k * (3 * k - 1) // 2]
            if k * (3 * k + 1) // 2 <= n:
                s += sign * p[n - k * (3 * k + 1) // 2]
            k += 1
        p[n] = s
    return p


def partitions_by_product(n_max: int) -> list:
    """Dieselben Zahlen über das Produkt der Faktoren 1/(1 − zᵏ) (Stück 5)."""
    c = [1] + [0] * n_max
    for k in range(1, n_max + 1):
        for n in range(k, n_max + 1):
            c[n] += c[n - k]
    return c


# ----------------------------------------------------------------------------- Gleichung F = 1 + Σ c·zʲ·Fᵏ (Stück 3)

def spec_terms(c1: int, c2: int, c3: int) -> list:
    """Die eigene Gleichung F = 1 + c1·z·F + c2·z·F² + c3·z²·F² als Liste (Koeffizient, j, k); Terme mit Koeffizient 0 entfallen."""
    return [t for t in ((c1, 1, 1), (c2, 1, 2), (c3, 2, 2)) if t[0] > 0]


def spec_coefficients(terms, n_max: int) -> list:
    """Koeffizienten von F = 1 + Σ c z^j F^k (k <= 3) online: F[n] = Σ c·P_k[n−j] mit den Potenzen P_k = F^k."""
    for c, j, k in terms:
        if not (c >= 0 and j >= 1 and 1 <= k <= 3):
            raise ValueError(f"Term {(c, j, k)}: verlangt c >= 0, j >= 1, 1 <= k <= 3")
    f, p2, p3 = [1], [1], [1]
    powers = {1: f, 2: p2, 3: p3}
    for n in range(1, n_max + 1):
        total = 0
        for c, j, k in terms:
            if n - j >= 0:
                total += c * powers[k][n - j]
        f.append(total)
        p2.append(sum(f[i] * f[n - i] for i in range(n + 1)))
        p3.append(sum(f[i] * p2[n - i] for i in range(n + 1)))
    return f


def spec_by_substitution(terms, n_max: int) -> list:
    """Dieselben Koeffizienten durch wiederholtes Einsetzen F ← 1 + Σ c zʲ Fᵏ in abgeschnittene Reihen (nur für kleine n_max gedacht)."""
    def mul(a, b):
        out = [0] * (n_max + 1)
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b[: n_max + 1 - i]):
                    out[i + j] += x * y
        return out

    f = [1] + [0] * n_max
    for _ in range(n_max + 1):
        new = [1] + [0] * n_max
        for c, j, k in terms:
            power = [1] + [0] * n_max
            for _ in range(k):
                power = mul(power, f)
            for i in range(n_max + 1 - j):
                new[i + j] += c * power[i]
        f = new
    return f


def phi(terms, z, y):
    return 1 + sum(c * z ** j * y ** k for c, j, k in terms)


def phi_y(terms, z, y):
    return sum(c * k * z ** j * y ** (k - 1) for c, j, k in terms)


def phi_z(terms, z, y):
    return sum(c * j * z ** (j - 1) * y ** k for c, j, k in terms)


def phi_yy(terms, z, y):
    return sum(c * k * (k - 1) * z ** j * y ** (k - 2) for c, j, k in terms if k >= 2)


def is_nonlinear(terms) -> bool:
    return any(k >= 2 for _, _, k in terms)


def is_periodic(terms) -> bool:
    """Alle Terme haben einen Exponenten j, der ein Vielfaches von p > 1 ist: nur Größen, die durch p teilbar sind, kommen vor."""
    if not terms:
        return False
    g = 0
    for _, j, _ in terms:
        g = math.gcd(g, j)
    return g > 1


def solve_system(terms) -> tuple:
    """(ρ, τ): τ = Φ(ρ, τ) und Φ_y(ρ, τ) = 1; kleinste Lösung mit τ > 1 (Scan in τ, Bisektion in z und in τ). Verlangt eine nichtlineare, aperiodische Gleichung."""
    if not is_nonlinear(terms):
        raise ValueError("linear: keine Wurzelsingularität")

    def z_of(tau):
        lo, hi = 0.0, 1.0
        while phi_y(terms, hi, tau) < 1:
            hi *= 2
        for _ in range(200):
            mid = (lo + hi) / 2
            if phi_y(terms, mid, tau) < 1:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    h = lambda tau: phi(terms, z_of(tau), tau) - tau
    tau = 1.0
    prev = h(tau)
    while tau < 1e9:
        nxt = tau * 1.02
        val = h(nxt)
        if prev > 0 >= val:
            lo, hi = tau, nxt
            for _ in range(200):
                mid = (lo + hi) / 2
                if h(mid) > 0:
                    lo = mid
                else:
                    hi = mid
            t = (lo + hi) / 2
            return z_of(t), t
        tau, prev = nxt, val
    raise RuntimeError("keine Singularität gefunden")


def amplitude(terms) -> tuple:
    """(ρ, τ, γ) mit F ≈ τ − γ·√(1 − z/ρ), γ = √(2ρ·Φ_z / Φ_yy); der Koeffizient ist dann ~ γ/(2√π)·ρ⁻ⁿ·n^(−3/2)."""
    rho, tau = solve_system(terms)
    gamma = math.sqrt(2 * rho * phi_z(terms, rho, tau) / phi_yy(terms, rho, tau))
    return rho, tau, gamma


# ----------------------------------------------------------------------------- Transfersatz, Quotient, Richardson

def binomial_coefficient(a: float, n: int) -> float:
    """Koeffizient von zⁿ in (1 − z)^(−a): Produkt (k − 1 + a)/k, k = 1..n."""
    coef = 1.0
    for k in range(1, n + 1):
        coef *= (k - 1 + a) / k
    return coef


def transfer_lead(a: float, n: int) -> float:
    """Führender Term des Transfersatzes: n^(a−1)/Γ(a)."""
    return n ** (a - 1) / math.gamma(a)


def transfer_error(a: float, n: int) -> float:
    """Relativer Fehler (exakt / führender Term − 1); strebt gegen a(a−1)/(2n)."""
    return binomial_coefficient(a, n) / transfer_lead(a, n) - 1


def ratio(c, n: int) -> Fraction:
    """Quotient c(n+1)/c(n)."""
    return Fraction(c[n + 1], c[n]) if not isinstance(c[n], Fraction) else c[n + 1] / c[n]


def richardson(c, n: int) -> Fraction:
    """μ̂ = (n+1)·r(n+1) − n·r(n): beseitigt den 1/n-Term des Quotienten."""
    return (n + 1) * ratio(c, n + 1) - n * ratio(c, n)


def exponent_estimate(c, n: int, mu) -> float:
    """α̂ = n·(r(n)/μ − 1): Schätzung des Exponenten, wenn c(n) ~ K·μⁿ·n^α."""
    return n * (float(ratio(c, n)) / float(mu) - 1)


def predict_with_exponent(c, n_fit: int, mu: float, alpha: float, n_target: int) -> float:
    """Wert c(n_target)/exakt, wenn K bei n_fit angepasst und mit dem Exponent α und der Rate μ fortgeschrieben wird: Quotient Vorhersage / exakt."""
    k = ln(c[n_fit]) - (n_fit * math.log(mu) + alpha * math.log(n_fit))
    pred = k + n_target * math.log(mu) + alpha * math.log(n_target)
    return math.exp(pred - ln(c[n_target]))


def hardy_ramanujan_log(n: int) -> float:
    """Logarithmus des führenden Terms exp(π√(2n/3))/(4n√3) von p(n)."""
    return math.pi * math.sqrt(2 * n / 3) - math.log(4 * n * math.sqrt(3))
