"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import math

import plotly.graph_objects as go

import asy_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_error(rows: list[dict], title: str = "Betrag des relativen Fehlers", power: float = 1.0):
    """Fehler des führenden Terms und mit Korrektur gegen n (logarithmische Achsen), dazu die Linie n^(−power): 1/n, bei den Partitionen 1/√n."""
    fig = go.Figure()
    ns = [r["n"] for r in rows if r["Fehler"] is not None and r["Fehler"] != 0]
    if ns:
        fig.add_trace(go.Scatter(x=ns, y=[abs(r["Fehler"]) for r in rows if r["n"] in ns], mode="lines+markers", name="führender Term", line=dict(color=C.COLOR_MAIN)))
        corr = [r for r in rows if r["Fehler mit Korrektur"] not in (None, 0)]
        if corr:
            fig.add_trace(go.Scatter(x=[r["n"] for r in corr], y=[abs(r["Fehler mit Korrektur"]) for r in corr], mode="lines+markers", name="mit Korrektur (1 + B/n)", line=dict(color=C.COLOR_LINE)))
        first = rows[0]["n"]
        fig.add_trace(go.Scatter(x=ns, y=[abs(rows[0]["Fehler"] or 1.0) * (first / n) ** power for n in ns], mode="lines", name="Linie ∝ 1/n" if power == 1.0 else "Linie ∝ 1/√n", line=dict(color=C.COLOR_ALL, dash="dash")))
    fig.update_xaxes(title_text="n", type="log")
    fig.update_yaxes(title_text=title, type="log")
    return _base(fig, 340)


def build_transfer(rows: list[dict]):
    """n mal Fehler des Transfersatzes je a gegen n (strebt gegen a(a−1)/2)."""
    fig = go.Figure()
    for a in dict.fromkeys(r["a"] for r in rows):
        sub = [r for r in rows if r["a"] == a]
        fig.add_trace(go.Scatter(x=[r["n"] for r in sub], y=[r["n·Fehler"] for r in sub], mode="lines+markers", name=f"a = {a:g} (a(a−1)/2 = {a * (a - 1) / 2:g})"))
    fig.update_xaxes(title_text="n", type="log")
    fig.update_yaxes(title_text="n mal Fehler")
    return _base(fig, 340)


def build_quotient(rows: list[dict]):
    """Fehler der Wachstumsrate: einfacher Quotient gegen Richardson, je Folge (logarithmische Achsen)."""
    fig = go.Figure()
    for name in dict.fromkeys(r["Folge"] for r in rows):
        sub = [r for r in rows if r["Folge"] == name]
        short = name.split(" (")[0]
        fig.add_trace(go.Scatter(x=[r["n"] for r in sub], y=[r["einfacher Quotient"] for r in sub], mode="lines+markers", name=f"{short}: Quotient"))
        fig.add_trace(go.Scatter(x=[r["n"] for r in sub], y=[max(r["Richardson"], 1e-12) for r in sub], mode="lines+markers", name=f"{short}: Richardson", line=dict(dash="dot")))
    fig.update_xaxes(title_text="n", type="log")
    fig.update_yaxes(title_text="Fehler der Wachstumsrate", type="log")
    return _base(fig, 360)


def build_spec_errors(res: dict):
    """n mal Fehler des führenden Terms je Zufallsgleichung (Streifen), für die drei Größen n."""
    fig = go.Figure()
    for n in C.SPEC_NS:
        row = next(r for r in res["rows"] if r["n"] == n)
        fig.add_trace(go.Bar(x=[f"n = {n}"], y=[row["mittleres n·Fehler"]], name=f"Mittel n = {n}", error_y=dict(type="data", symmetric=False, array=[row["größtes n·Fehler"] - row["mittleres n·Fehler"]],
                                                                                                   arrayminus=[row["mittleres n·Fehler"] - row["kleinstes n·Fehler"]])))
    fig.update_yaxes(title_text="n mal Fehler (Mittel und Bereich)")
    return _base(fig, 320)


def build_classes(rows: list[dict]):
    """Quotient c(n+1)/c(n) je Folge und n (logarithmische Achse): Grenzwert, Wachstum ohne Grenze oder Abfall gegen 1."""
    fig = go.Figure()
    ns = [f"n = {n}" for n in C.CLASS_NS]
    for r in rows:
        fig.add_trace(go.Scatter(x=ns, y=[r[k] for k in ns], mode="lines+markers", name=r["Folge"]))
    fig.update_yaxes(title_text="Quotient c(n+1)/c(n)", type="log")
    return _base(fig, 340)


def build_play(seq, n: int, mu: float):
    """Quotient c(k+1)/c(k) der eigenen Gleichung gegen k, mit der Wachstumsrate 1/ρ."""
    ks = list(range(1, min(n, len(seq) - 2) + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ks, y=[seq[k + 1] / seq[k] for k in ks], mode="lines", name="Quotient", line=dict(color=C.COLOR_MAIN)))
    fig.add_hline(y=mu, line=dict(color=C.COLOR_WARN, dash="dash"))
    fig.update_xaxes(title_text="n")
    fig.update_yaxes(title_text="c(n+1)/c(n)")
    return _base(fig, 320)
