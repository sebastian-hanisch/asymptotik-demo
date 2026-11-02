"""Kennzahlen, Experimente und Verdikte. Jedes Verdikt ist eine reine Funktion (Art, Text); die App ruft st.<Art>(Text)."""

import math
import random
from dataclasses import dataclass, field
from fractions import Fraction

import asy_algorithm as A
import asy_constants as C
from asy_scenario import FamilyInfo, effective_n, family_info, make_sequence

_SUPER = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


@dataclass(frozen=True)
class Settings:
    family: str = C.DEFAULT_FAMILY
    n: int = C.DEFAULT_N
    m: int = C.DEFAULT_M


@dataclass(frozen=True, eq=False)
class Analysis:
    settings: Settings
    n_eff: int
    info: FamilyInfo
    seq: list
    exact_ln: float                        # ln c(n)
    lead_ln: object                        # ln des führenden Terms (None: keiner)
    error: object                          # Näherung / exakt − 1 (None: keiner)
    corrected_error: object                # mit Korrekturfaktor (1 + B/n)
    quotient: float
    richardson: float
    mu_known: object                       # bekannte Wachstumsrate 1/ρ (None: unbekannt)
    alpha_hat: object                      # Schätzung des Exponenten
    ways: list                             # Rechenwege: {"Gruppe", "Weg", "Wert", "Text", "Schritte", "Grund"}
    rows: list                             # Fehlertabelle
    problems: list
    notes: list
    fit: object = None                     # (n_fit, μ̂, K̂) bei angepasster Näherung
    extras: dict = field(default_factory=dict)


# ----------------------------------------------------------------------------- Formatierung

def de(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f}".replace(".", ",").replace("-", "−")


def big_text(x: int) -> str:
    """Ganze Zahl lesbar: bis 12 Stellen mit Tausenderpunkt, darüber Mantisse mal Zehnerpotenz mit Stellenzahl (ohne Stringumwandlung der ganzen Zahl)."""
    if x < 10 ** 12:
        return f"{x:,}".replace(",", ".")
    d = A.digit_count(x)
    s = str(x // 10 ** (d - 3))
    return f"{s[0]},{s[1:3]}·10{str(d - 1).translate(_SUPER)} ({d} Stellen)"


def sci_text(x: float, digits: int = 2) -> str:
    """Gleitkommazahl als Mantisse mal Zehnerpotenz oder ohne Potenz, wenn sie klein genug ist."""
    if x == 0:
        return "0"
    if 0.01 <= abs(x) < 10000:
        return de(x, digits)
    mant, exp = f"{x:.{digits - 1}e}".split("e")
    return f"{mant.replace('.', ',').replace('-', '−')}·10{str(int(exp)).translate(_SUPER)}"


def ln_text(value_ln: float) -> str:
    """Zahl mit gegebenem natürlichem Logarithmus als Mantisse mal Zehnerpotenz (auch weit über der Gleitkommagrenze)."""
    log10 = value_ln / math.log(10)
    exp = math.floor(log10)
    mant = 10 ** (log10 - exp)
    return f"{de(mant, 2)}·10{str(exp).translate(_SUPER)}"


def percent(x: float, digits: int = 3) -> str:
    return de(100 * x, digits) + " %"


def percent_fine(x: float, digits: int = 5) -> str:
    """Prozent mit Nachkommastellen, bei winzigen Werten (unter 0,001 %) als Mantisse mal Zehnerpotenz, damit nicht „0,00000 %“ dasteht."""
    return percent(x, digits) if abs(100 * x) >= 0.001 else sci_text(100 * x, 3) + " %"


def value_text(a_seq, n: int) -> str:
    x = a_seq[n]
    return big_text(x) if isinstance(x, int) else ln_text(A.ln(x))


# ----------------------------------------------------------------------------- führender Term

def lead_log(info: FamilyInfo, n: int):
    """ln des führenden Terms A·ρ⁻ⁿ·n^α, wenn Lage, Exponent und Amplitude bekannt sind; für die Partitionen die Näherung von Hardy und Ramanujan."""
    if info.name == "Partitionen":
        return A.hardy_ramanujan_log(n)
    if info.rho is None or info.amp is None or info.alpha is None:
        return None
    return math.log(info.amp) - n * math.log(info.rho) + info.alpha * math.log(n)


def corrected_log(info: FamilyInfo, n: int):
    ll = lead_log(info, n)
    if ll is None or info.correction is None:
        return None
    return ll + math.log1p(float(info.correction) / n)


# ----------------------------------------------------------------------------- Analyse der eingestellten Familie

def analyse(s: Settings) -> Analysis:
    n = effective_n(s.family, s.n)
    m = max(C.M_MIN, min(s.m, C.M_MAX))
    info = family_info(s.family, m)
    notes = []
    if n != s.n:
        notes.append(f"Für diese Familie rechnet die App höchstens bis n = {C.N_CAP[s.family]}: gerechnet wird mit n = {n}.")
    seq = make_sequence(s.family, m, n + 2)
    exact_ln = A.ln(seq[n])
    ways, problems = [], []

    def add(group, name, value, text, steps=None):
        ways.append({"Gruppe": group, "Weg": name, "Wert": value, "Text": text, "Schritte": steps, "Grund": ""})

    def skipped(group, name, reason):
        ways.append({"Gruppe": group, "Weg": name, "Wert": None, "Text": "", "Schritte": None, "Grund": reason})

    main_name = {"Catalan": "Formel C(2n,n)/(n+1)", "Motzkin": "Rekursion der Motzkin-Zahlen", "Zentraler Binomialkoeffizient": "Binomialkoeffizient C(2n,n)", "Fibonacci-Pole": "Faltung der Fibonacci-Folge",
                 "Wurzelbäume ohne Reihenfolge": "Rekursion T = z·MSET(T)", "Beschriftete Wurzelbäume": "Formel nⁿ⁻¹/n!", "Bell-Zahlen": "Bell-Dreieck", "Partitionen": "Fünfeckszahlen-Rekursion"}[s.family]
    add("Koeffizient", main_name, seq[n], value_text(seq, n))
    if s.family == "Catalan":
        other = A.spec_coefficients([(1, 1, 2)], n)[n]
        add("Koeffizient", "Gleichung F = 1 + z·F² (online)", other, big_text(other))
    elif s.family == "Motzkin":
        other = A.spec_coefficients([(1, 1, 1), (1, 2, 2)], n)[n]
        add("Koeffizient", "Gleichung F = 1 + z·F + z²·F² (online)", other, big_text(other))
    elif s.family == "Zentraler Binomialkoeffizient":
        c = 1
        for k in range(1, n + 1):
            c = c * (4 * k - 2) // k
        add("Koeffizient", "Rekursion c(k) = c(k−1)·(4k−2)/k", c, big_text(c))
    elif s.family == "Fibonacci-Pole":
        other = A.fibonacci_pole_by_division(m, n)[n]
        add("Koeffizient", f"{m}-faches Teilen durch 1 − z − z²", other, big_text(other))
    elif s.family == "Wurzelbäume ohne Reihenfolge":
        k = min(n, C.ENUM_TREE_N)
        count = A.trees_canonical_count(k)
        group = f"Koeffizient bei n = {k}"
        add(group, "Rekursion T = z·MSET(T)", seq[k], big_text(seq[k]))
        add(group, "Aufzählen kanonischer Formen", count, big_text(count))
    elif s.family == "Beschriftete Wurzelbäume":
        if n <= C.EGF_CHECK_N:
            counts = A.labelled_trees_counts(n)
            other = Fraction(counts[n], math.factorial(n))
            add("Koeffizient", "Kalkül T = z·exp(T) (Stück 6)", other, ln_text(A.ln(other)))
        else:
            skipped("Koeffizient", "Kalkül T = z·exp(T) (Stück 6)", f"nur bis n = {C.EGF_CHECK_N}")
    elif s.family == "Bell-Zahlen":
        if n <= C.EGF_CHECK_N:
            other = A.bell_by_exp(n)[n]
            add("Koeffizient", "exp-Kalkül (Stück 6)", other, big_text(other))
        else:
            skipped("Koeffizient", "exp-Kalkül (Stück 6)", f"nur bis n = {C.EGF_CHECK_N}")
    else:
        other = A.partitions_by_product(n)[n]
        add("Koeffizient", "Produkt der Faktoren 1/(1 − zᵏ) (Stück 5)", other, big_text(other))

    # --- Lage und Konstante aus dem System (nur algebraische Gleichungen)
    extras = {}
    system = {"Catalan": [(1, 1, 2)], "Motzkin": [(1, 1, 1), (1, 2, 2)]}.get(s.family)
    if system is not None:
        rho, tau, gamma = A.amplitude(system)
        extras["system"] = (rho, tau, gamma)
        if abs(A.phi(system, rho, tau) - tau) > 1e-9 or abs(A.phi_y(system, rho, tau) - 1) > 1e-9:
            problems.append("(ρ, τ) erfüllt das System nicht")
        if abs(rho - info.rho) > 1e-12 or abs(gamma / (2 * math.sqrt(math.pi)) - info.amp) > 1e-12:
            problems.append("Lage oder Amplitude aus dem System weichen von der geschlossenen Form ab")
    for group in dict.fromkeys(w["Gruppe"] for w in ways):
        done = [w for w in ways if w["Gruppe"] == group and w["Wert"] is not None]
        if any(w["Wert"] != done[0]["Wert"] for w in done):
            problems.append(f"{group}: " + ", ".join(w["Weg"] for w in done) + " weichen ab")

    # --- Näherung, Quotient, Richardson
    fit = None
    lead_ln_n = lead_log(info, n)
    if s.family == "Wurzelbäume ohne Reihenfolge":
        n0 = max(C.N_MIN, n // 2)
        mu0 = float(A.richardson(seq, n0))
        k0 = A.ln(seq[n0]) - (n0 * math.log(mu0) + info.alpha * math.log(n0))
        lead_ln_n = k0 + n * math.log(mu0) + info.alpha * math.log(n)
        fit = (n0, mu0, math.exp(k0))
    error = None if lead_ln_n is None else math.exp(lead_ln_n - exact_ln) - 1
    corr = corrected_log(info, n)
    corrected_error = None if corr is None else math.exp(corr - exact_ln) - 1
    quotient = float(A.ratio(seq, n))
    rich = float(A.richardson(seq, n))
    mu_known = None if info.rho is None else 1 / info.rho
    alpha_hat = None
    if mu_known is not None:
        alpha_hat = A.exponent_estimate(seq, n, mu_known)
    elif s.family == "Wurzelbäume ohne Reihenfolge":
        alpha_hat = A.exponent_estimate(seq, n, rich)

    rows = []
    grid = sorted({g for g in C.ERROR_GRID if g <= n} | {n})
    for g in grid:
        lg = lead_log(info, g)
        if s.family == "Wurzelbäume ohne Reihenfolge":
            g0 = max(C.N_MIN, g // 2)
            if g0 == g:
                lg = None                                      # Anpassung und Vorhersage fielen auf dieselbe Stelle
            else:
                mu_g = float(A.richardson(seq, g0))
                kk = A.ln(seq[g0]) - (g0 * math.log(mu_g) + info.alpha * math.log(g0))
                lg = kk + g * math.log(mu_g) + info.alpha * math.log(g)
        e = None if lg is None else math.exp(lg - A.ln(seq[g])) - 1
        cg = corrected_log(info, g)
        ce = None if cg is None else math.exp(cg - A.ln(seq[g])) - 1
        scale = math.sqrt(g) if s.family == "Partitionen" else g
        rows.append({"n": g, "Fehler": e, "skaliert": None if e is None else scale * e, "Fehler mit Korrektur": ce})
    extras["scale_name"] = "√n mal Fehler" if s.family == "Partitionen" else "n mal Fehler"
    return Analysis(s, n, info, seq, exact_ln, lead_ln_n, error, corrected_error, quotient, rich, mu_known, alpha_hat, ways, rows, problems, notes, fit, extras)


def way_rows(a: Analysis) -> list[dict]:
    """Tabelle der Rechenwege: Frage, Weg, Ergebnis, Prüfung."""
    rows = []
    reference = {}
    for w in a.ways:
        if w["Wert"] is not None and w["Gruppe"] not in reference:
            reference[w["Gruppe"]] = w["Wert"]
    for w in a.ways:
        if w["Wert"] is None:
            rows.append({"Frage": w["Gruppe"], "Weg": w["Weg"], "Ergebnis": "–", "Prüfung": w["Grund"]})
        else:
            rows.append({"Frage": w["Gruppe"], "Weg": w["Weg"], "Ergebnis": w["Text"], "Prüfung": "gleich" if w["Wert"] == reference[w["Gruppe"]] else "weicht ab"})
    return rows


def error_rows(a: Analysis) -> list[dict]:
    """Fehlertabelle: Fehler des führenden Terms und mit Korrektur, für die Stützstellen bis n."""
    def fmt(x):
        return "–" if x is None else sci_text(100 * x, 3) + " %"

    return [{"n": r["n"], "Fehler des führenden Terms": fmt(r["Fehler"]), a.extras["scale_name"]: "–" if r["skaliert"] is None else de(r["skaliert"], 4), "Fehler mit Korrektur": fmt(r["Fehler mit Korrektur"])} for r in a.rows]


def verdict_answers(a: Analysis):
    if a.problems:
        return "error", "Die Rechenwege widersprechen sich: " + "; ".join(a.problems)
    info = a.info
    n = a.n_eff
    if info.alpha is None:
        if info.name == "Bell-Zahlen":
            r_ratio = a.quotient / (n / math.log(n))
            return "warning", (f"Bell-Zahlen: keine Wachstumsrate. Der Quotient B(n+1)/B(n) ist bei n = {n} schon {de(a.quotient, 2)} und wächst weiter (etwa das {de(r_ratio, 2)}-fache von n/ln n); "
                               "die erzeugende Funktion ist überall konvergent und hat keine Singularität im Endlichen. Dafür braucht man die Sattelpunktmethode.")
        e = a.error
        return "warning", (f"Partitionen: keine Wachstumsrate. Der Quotient p(n+1)/p(n) ist bei n = {n} {de(a.quotient, 4)} und strebt gegen 1 (subexponentiell). "
                           f"Der führende Term von Hardy und Ramanujan exp(π√(2n/3))/(4n√3) liegt {percent(e, 2)} über dem exakten Wert (Fehler mal √n ≈ {de(e * math.sqrt(n), 3)}); "
                           "die wesentliche Singularität bei z = 1 braucht die Kreismethode.")
    rho_text = f"ρ = {de(info.rho, 6)}, " if info.rho is not None else ""
    if info.rho is None:
        mu = a.richardson
        fit = a.fit
        return "success", (f"{info.name}: nicht aus einer Gleichung ablesbar. Wachstumskonstante nach Richardson μ̂ = {de(mu, 6)} (einfacher Quotient {de(a.quotient, 6)}), Exponent n(r/μ̂ − 1) = {de(a.alpha_hat, 4)} (erwartet −1,5). "
                           f"Die Näherung c ≈ K·μ̂ⁿ·n^(−3/2) mit bei n = {fit[0]} angepasstem K liegt bei n = {n} {percent(a.error, 4)} neben dem exakten Wert.")
    head = f"{info.name} ({info.kind}): {rho_text}Wachstumsrate 1/ρ = {de(a.mu_known, 6)}, Exponent {de(info.alpha, 1)}."
    err = f"Der führende Term liegt bei n = {n} {percent(a.error, 4)} neben dem exakten Wert"
    if a.corrected_error is not None:
        err += f", mit Korrekturfaktor (1 + B/n), B = {de(float(info.correction), 4)}, nur noch {percent_fine(a.corrected_error, 5)}"
    quot = (f" Der einfache Quotient hat den Fehler {sci_text(abs(a.quotient - a.mu_known), 2)}, die Richardson-Schätzung {sci_text(abs(a.richardson - a.mu_known), 2)}.")
    return "success", f"{head} {err}.{quot}"


# ----------------------------------------------------------------------------- Experiment 2: Transfersatz

def transfer_rows() -> list[dict]:
    rows = []
    for a in C.TRANSFER_AS:
        for n in C.TRANSFER_NS:
            e = A.transfer_error(a, n)
            rows.append({"a": a, "n": n, "Fehler": e, "n·Fehler": n * e, "a(a−1)/2": a * (a - 1) / 2})
    return rows


def verdict_transfer(rows: list[dict]):
    worst = max(abs(r["n·Fehler"] - r["a(a−1)/2"]) for r in rows if r["n"] == max(C.TRANSFER_NS))
    if worst > 0.01:
        return "error", f"n·Fehler weicht bei n = {max(C.TRANSFER_NS)} um {de(worst, 4)} von a(a−1)/2 ab."
    return "success", (f"Für (1 − z)^(−a) ist der exakte Koeffizient n^(a−1)/Γ(a)·(1 + a(a−1)/(2n) + …): bei n = {max(C.TRANSFER_NS)} weicht n·Fehler höchstens {de(worst, 4)} von a(a−1)/2 ab, "
                       "für a = 1 (geometrische Reihe) ist die Näherung exakt.")


# ----------------------------------------------------------------------------- Experiment 3: Quotient gegen Richardson

def quotient_rows() -> dict:
    rows = []
    cat, mot = A.catalan(max(C.QUOTIENT_NS) + 2), A.motzkin(max(C.QUOTIENT_NS) + 2)
    trees = A.unlabelled_trees(C.QUOTIENT_TREE_REF + 2)
    ref = float(A.richardson(trees, C.QUOTIENT_TREE_REF))
    for name, seq, mu in (("Catalan (Rate 4)", cat, 4.0), ("Motzkin (Rate 3)", mot, 3.0), ("Wurzelbäume ohne Reihenfolge (Rate aus n = %d)" % C.QUOTIENT_TREE_REF, trees, ref)):
        for n in C.QUOTIENT_NS:
            rows.append({"Folge": name, "n": n, "einfacher Quotient": abs(float(A.ratio(seq, n)) - mu), "Richardson": abs(float(A.richardson(seq, n)) - mu)})
    return {"rows": rows, "tree_ref": ref}


def doubling_factors(rows: list[dict], name: str, key: str) -> list[float]:
    sub = [r for r in rows if r["Folge"] == name]
    return [sub[i][key] / sub[i + 1][key] for i in range(len(sub) - 1)]


def verdict_quotient(res: dict):
    rows = res["rows"]
    name = rows[0]["Folge"]
    plain = doubling_factors(rows, name, "einfacher Quotient")
    rich = doubling_factors(rows, name, "Richardson")
    last = [r for r in rows if r["Folge"] == name][-1]
    kind = "success" if 1.7 < min(plain) and max(plain) < 2.3 and 3.3 < min(rich) and max(rich) < 4.7 else "warning"
    return kind, (f"{name}: beim Verdoppeln von n sinkt der Fehler des einfachen Quotienten um den Faktor {de(min(plain), 2)} bis {de(max(plain), 2)} (Ordnung 1), der Richardson-Schätzung um {de(min(rich), 2)} bis {de(max(rich), 2)} (Ordnung 2); "
                  f"bei n = {last['n']}: {sci_text(last['einfacher Quotient'], 2)} gegen {sci_text(last['Richardson'], 2)}, etwa {de(last['einfacher Quotient'] / last['Richardson'], 0)}-mal genauer.")


# ----------------------------------------------------------------------------- Experiment 4: von der Gleichung zur Konstanten

def random_spec(rng) -> list:
    terms = [(rng.randint(1, 3), 1, rng.randint(1, 3))]
    for _ in range(rng.randint(1, 3)):
        terms.append((rng.randint(1, 3), rng.randint(1, 3), rng.randint(1, 3)))
    if not any(k >= 2 for _, _, k in terms):
        terms.append((rng.randint(1, 3), rng.randint(1, 3), 2))
    return terms


def spec_experiment() -> dict:
    rng = random.Random(C.SPEC_SEED)
    n_top = max(C.SPEC_NS)
    errors = {n: [] for n in C.SPEC_NS}
    plain, rich = [], []
    specs = []
    for _ in range(C.SPEC_COUNT):
        terms = random_spec(rng)
        rho, tau, gamma = A.amplitude(terms)
        f = A.spec_coefficients(terms, n_top + 2)
        amp = gamma / (2 * math.sqrt(math.pi))
        for n in C.SPEC_NS:
            errors[n].append(math.exp(math.log(amp) - n * math.log(rho) - 1.5 * math.log(n) - A.ln(f[n])) - 1)
        plain.append(abs(float(A.ratio(f, n_top)) * rho - 1))
        rich.append(abs(float(A.richardson(f, n_top)) * rho - 1))
        specs.append({"terms": terms, "rho": rho, "tau": tau, "gamma": gamma})
    rows = []
    for n in C.SPEC_NS:
        e = errors[n]
        rows.append({"n": n, "mittlerer Fehler": sum(abs(x) for x in e) / len(e), "größter Fehler": max(abs(x) for x in e), "mittleres n·Fehler": sum(n * x for x in e) / len(e),
                     "kleinstes n·Fehler": min(n * x for x in e), "größtes n·Fehler": max(n * x for x in e)})
    return {"rows": rows, "specs": specs, "plain": plain, "rich": rich, "n_top": n_top}


def verdict_spec(res: dict):
    rows = res["rows"]
    last = rows[-1]
    n = res["n_top"]
    mean_plain, mean_rich = sum(res["plain"]) / len(res["plain"]), sum(res["rich"]) / len(res["rich"])
    if not all(rows[i]["mittlerer Fehler"] > rows[i + 1]["mittlerer Fehler"] for i in range(len(rows) - 1)):
        return "warning", "Der mittlere Fehler des führenden Terms fällt nicht bei allen n."
    return "success", (f"Bei {len(res['specs'])} zufälligen Gleichungen trifft der führende Term γ/(2√π)·ρ⁻ⁿ·n^(−3/2) aus dem System bei n = {last['n']} im Mittel auf {percent(last['mittlerer Fehler'], 2)} (größter Fehler {percent(last['größter Fehler'], 2)}); "
                       f"der Fehler halbiert sich mit n. Der einfache Quotient hat bei n = {n} bei allen Gleichungen den Fehler {de(mean_plain, 4)} (≈ 3/(2n) = {de(1.5 / n, 4)}), die Richardson-Schätzung im Mittel {sci_text(mean_rich, 2)}.")


# ----------------------------------------------------------------------------- Experiment 5: Wachstumsklassen und falscher Exponent

def class_rows() -> list[dict]:
    top = max(C.CLASS_NS) + 1
    seqs = {"Catalan (Wurzelsingularität)": A.catalan(top), "Fibonacci (Pol)": A.fibonacci_pole(1, top), "Bell-Zahlen (ganze Funktion)": A.bell(top),
            "Partitionen (wesentliche Singularität)": A.partitions(top), "n! (Fakultät)": [math.factorial(k) for k in range(top + 1)]}
    rows = []
    for name, seq in seqs.items():
        row = {"Folge": name}
        for n in C.CLASS_NS:
            row[f"n = {n}"] = float(Fraction(seq[n + 1], seq[n]))
        rows.append(row)
    return rows


def class_verdict(rows: list[dict]):
    by = {r["Folge"]: r for r in rows}
    ns = [f"n = {n}" for n in C.CLASS_NS]
    cat, bell, part = by["Catalan (Wurzelsingularität)"], by["Bell-Zahlen (ganze Funktion)"], by["Partitionen (wesentliche Singularität)"]
    return "warning", (f"Der Quotient c(n+1)/c(n) verrät die Klasse: Catalan strebt gegen 4 ({de(cat[ns[0]], 2)}, {de(cat[ns[1]], 3)}, {de(cat[ns[2]], 3)}), die Bell-Zahlen wachsen ohne Grenze ({de(bell[ns[0]], 1)}, {de(bell[ns[1]], 1)}, {de(bell[ns[2]], 1)}), "
                       f"die Partitionen fallen gegen 1 ({de(part[ns[0]], 3)}, {de(part[ns[1]], 3)}, {de(part[ns[2]], 3)}). Eine Wachstumsrate gibt es nur im ersten Fall.")


def wrong_exponent_rows() -> list[dict]:
    cat = A.catalan(C.WRONG_TARGET_N)
    return [{"Exponent": alpha, "Vorhersage / exakt": A.predict_with_exponent(cat, C.WRONG_FIT_N, 4.0, alpha, C.WRONG_TARGET_N)} for alpha in C.WRONG_ALPHAS]


def verdict_wrong(rows: list[dict]):
    pick = {r["Exponent"]: r["Vorhersage / exakt"] for r in rows}
    return "warning", (f"Catalan, Konstante bei n = {C.WRONG_FIT_N} angepasst, Vorhersage für n = {C.WRONG_TARGET_N}: mit dem richtigen Exponent −1,5 liegt sie um {percent(abs(pick[-1.5] - 1), 1)} daneben, "
                       f"mit −0,5 um den Faktor {de(pick[-0.5], 1)}, mit 0 um den Faktor {de(pick[0.0], 1)}, mit −2,5 um den Faktor {de(pick[-2.5], 3)}: der Exponent entscheidet.")


# ----------------------------------------------------------------------------- Spielwiese: eigene Gleichung

def play_equation(c1: int, c2: int, c3: int, n: int) -> dict:
    c1, c2, c3 = (max(0, min(c, C.PLAY_C_MAX)) for c in (c1, c2, c3))
    n = max(C.PLAY_N_MIN, min(n, C.PLAY_N_MAX))
    terms = A.spec_terms(c1, c2, c3)
    res = {"terms": terms, "n": n, "equation": equation_text(c1, c2, c3)}
    if not terms:
        res.update(kind="trivial", seq=[1] + [0] * (n + 2))
        return res
    if A.is_periodic(terms):
        res.update(kind="periodic")
        return res
    seq = A.spec_coefficients(terms, n + 2)
    res["seq"] = seq
    if not A.is_nonlinear(terms):
        res.update(kind="pole", rho=1 / c1, mu=float(c1), alpha=0.0, amp=1.0, error=math.exp(0 - A.ln(seq[n]) + n * math.log(c1)) - 1)
        return res
    rho, tau, gamma = A.amplitude(terms)
    amp = gamma / (2 * math.sqrt(math.pi))
    err = math.exp(math.log(amp) - n * math.log(rho) - 1.5 * math.log(n) - A.ln(seq[n])) - 1
    res.update(kind="root", rho=rho, tau=tau, gamma=gamma, amp=amp, mu=1 / rho, error=err, n_error=n * err, quotient=float(A.ratio(seq, n)), richardson=float(A.richardson(seq, n)))
    return res


def equation_text(c1: int, c2: int, c3: int) -> str:
    def coef(c):
        return "" if c == 1 else str(c)

    parts = ["1"]
    if c1:
        parts.append(f"{coef(c1)}z·F")
    if c2:
        parts.append(f"{coef(c2)}z·F²")
    if c3:
        parts.append(f"{coef(c3)}z²·F²")
    return "F = " + " + ".join(parts)


def verdict_play(res: dict):
    if res["kind"] == "trivial":
        return "info", "Alle Koeffizienten sind 0: F = 1, es gibt nur die leere Struktur (keine Singularität, nichts wächst)."
    if res["kind"] == "periodic":
        return "warning", ("Die Gleichung hat nur Terme mit z²: es kommen nur gerade Größen vor (Periode 2, Stück 3). Der Quotient c(n+1)/c(n) ist dann 0; die App rechnet die Asymptotik für aperiodische Gleichungen "
                           "(mindestens ein Term mit z¹).")
    if res["kind"] == "pole":
        mu = int(res["mu"])
        denominator = "1 − z" if mu == 1 else f"1 − {mu}z"
        return "success", (f"Die Gleichung ist linear: F = 1/({denominator}), c(n) = {mu}ⁿ. Pol bei ρ = {de(res['rho'], 6)}, Exponent 0; die Näherung ist exakt, kein Wurzelverhalten.")
    return "success", (f"{res['equation']}: ρ = {de(res['rho'], 6)}, τ = {de(res['tau'], 6)}, γ = {de(res['gamma'], 6)}; c(n) ≈ γ/(2√π)·ρ⁻ⁿ·n^(−3/2) mit Amplitude {de(res['amp'], 6)}. "
                       f"Bei n = {res['n']} liegt der führende Term {percent(res['error'], 3)} neben dem exakten Wert (n mal Fehler = {de(res['n_error'], 3)}); Quotient {de(res['quotient'], 5)} gegen 1/ρ = {de(res['mu'], 5)}, Richardson {de(res['richardson'], 5)}.")
