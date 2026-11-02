"""Asymptotik – Lage und Art der Singularität - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 9 der Reihe „Abzählen und erzeugende Funktionen“: Wie schnell wächst eine Zählfolge, und wie gut ist die Näherung? Die nächste Singularität der erzeugenden Funktion bestimmt die
Wachstumsrate (Lage), den polynomiellen Faktor (Art) und, aus dem System, die Konstante; der Fehler fällt wie 1/n, Richardson-Extrapolation macht die Schätzung der Rate viel besser.
Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import asy_constants as C
from asy_evaluation import (
    Settings,
    analyse,
    class_rows,
    class_verdict,
    de,
    doubling_factors,
    error_rows,
    play_equation,
    quotient_rows,
    sci_text,
    spec_experiment,
    transfer_rows,
    verdict_answers,
    verdict_play,
    verdict_quotient,
    verdict_spec,
    verdict_transfer,
    verdict_wrong,
    way_rows,
    wrong_exponent_rows,
)
from asy_layout import dunkles_design, kopf_css
from asy_pdf_export import build_pdf
from asy_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sidebar_presets,
    sync_query_params,
)
from asy_visualization import build_classes, build_error, build_play, build_quotient, build_spec_errors, build_transfer

st.set_page_config(page_title="Asymptotik – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _transfer():
    return transfer_rows()


@st.cache_data(show_spinner=False)
def _quotient():
    return quotient_rows()


@st.cache_data(show_spinner=False)
def _specs():
    return spec_experiment()


@st.cache_data(show_spinner=False)
def _classes():
    return class_rows(), wrong_exponent_rows()


@st.cache_data(show_spinner=False)
def _play(c1, c2, c3, n):
    return play_equation(c1, c2, c3, n)


def verdict(pair):
    kind, text = pair
    getattr(st, kind)(text)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in asy_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("📈 Asymptotik – Lage und Art der Singularität")
st.markdown(
    """
**Wie schnell wächst die Zahl, und wie gut ist die Näherung?** Die erzeugende Funktion verrät es, ohne die Zahlen zu rechnen: Die **nächste Singularität** $\\rho$ (der Punkt, an dem die Reihe nicht mehr konvergiert) bestimmt die
**Wachstumsrate** $1/\\rho$, ihre **Art** den **polynomiellen Faktor** (Wurzel: $n^{-3/2}$, Pol der Vielfachheit $m$: $n^{m-1}$), und das **Gleichungssystem** aus Stück 3 liefert die **Konstante**. Der **Transfersatz** macht daraus
$[z^n] F \\sim \\frac{\\gamma}{2\\sqrt{\\pi}}\\, \\rho^{-n} n^{-3/2}$. Der Fehler der Näherung fällt wie $1/n$ und ist messbar; der Quotient allein ist eine schlechte Schätzung der Rate, mit **Richardson-Extrapolation** wird er viel besser.
Und nicht jede Reihe hat eine Rate: bei ganzen Funktionen (Bell-Zahlen) und wesentlichen Singularitäten (Partitionen) wächst der Quotient ohne Grenze beziehungsweise fällt gegen 1.

Weiter unten: **fünf Experimente** (**🔬**), eine **🎲 Spielwiese**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert die Asymptotik aus der Singularität", expanded=True):
    st.markdown(
        """
1. **Lage:** Bei einer algebraischen Gleichung $F = \\Phi(z, F)$ liegt die Singularität dort, wo sich die Lösung verzweigt: $\\tau = \\Phi(\\rho, \\tau)$ und $\\Phi_y(\\rho, \\tau) = 1$ (Stück 3). Bei rationalen Reihen ist es die kleinste Nullstelle des Nenners (Stück 2).
2. **Art und Konstante:** Nahe $\\rho$ gilt $F \\approx \\tau - \\gamma \\sqrt{1 - z/\\rho}$ mit $\\gamma = \\sqrt{2 \\rho\\, \\Phi_z / \\Phi_{yy}}$; bei einem Pol der Vielfachheit $m$ gilt $F \\approx K (1 - z/\\rho)^{-m}$.
3. **Transfer:** $[z^n] (1 - z/\\rho)^{-a} = \\rho^{-n}\\, \\frac{n^{a-1}}{\\Gamma(a)} \\big(1 + \\tfrac{a(a-1)}{2n} + \\dots\\big)$: Wurzel ($a = -\\tfrac12$) gibt $n^{-3/2}$, Pol gibt $n^{m-1}$.
4. **Gegenprobe:** die exakten Zahlen auf zwei Wegen, der Quotient $c(n+1)/c(n)$ und die Richardson-Schätzung $\\hat\\mu = (n+1)\\, r(n+1) - n\\, r(n)$ gegen die Wachstumsrate.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Folge**")
    family = st.selectbox("Familie", list(C.FAMILIES), key="family_select", help="Welche Zählfolge: Wurzelsingularität (Catalan, Motzkin, Bäume), Pol (Fibonacci-Pole), oder keine Rate (Bell, Partitionen).")
    n = st.slider("Größe n", *bounds("n_slider"), key="n_slider", help=f"Index der Folge. Es wird höchstens bis {', '.join(f'{k} ({v})' for k, v in C.N_CAP.items() if v != C.N_MAX)} gerechnet, sonst bis {C.N_MAX}.")
    m = st.slider("Vielfachheit m (nur Fibonacci-Pole)", *bounds("m_slider"), key="m_slider", help="Die Reihe 1/(1 − z − z²)^m hat einen Pol der Vielfachheit m; der polynomielle Faktor ist n^(m−1).")

sync_query_params({"family_select": family, "n_slider": int(n), "m_slider": int(m)})

settings = Settings(family, int(n), int(m))
a = _analysis(settings)
for note in a.notes:
    st.info(note)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
info = a.info
m1, m2, m3, m4 = st.columns(4)
m1.metric(f"c({a.n_eff}) exakt", a.ways[0]["Text"], help="Der exakte Koeffizient (bei beschrifteten Bäumen der Koeffizient der exponentiellen erzeugenden Funktion nⁿ⁻¹/n!).")
m2.metric("Wachstumsrate 1/ρ", "keine" if a.mu_known is None and info.rho is None and a.settings.family != "Wurzelbäume ohne Reihenfolge" else de(a.mu_known if a.mu_known is not None else a.richardson, 6),
          help="Kehrwert der Lage der nächsten Singularität; bei den Wurzelbäumen ohne Reihenfolge die Richardson-Schätzung; ‚keine‘ bei Bell-Zahlen und Partitionen.")
m3.metric("Fehler des führenden Terms", "–" if a.error is None else de(100 * a.error, 4) + " %", help="Führender Term geteilt durch exakt minus 1; positiv heißt: die Näherung liegt zu hoch.")
m4.metric("Exponent", "–" if info.alpha is None else de(info.alpha, 1), help="Exponent α des polynomiellen Faktors n^α (Wurzel −3/2, im Nenner −1/2, Pol m − 1).")
st.plotly_chart(build_error(a.rows, power=0.5 if family == "Partitionen" else 1.0), width="stretch", key="main_chart")
st.caption("Betrag des relativen Fehlers des führenden Terms (und mit Korrekturfaktor) gegen n, beide Achsen logarithmisch; gestrichelt eine Linie ∝ 1/n (bei den Partitionen ∝ 1/√n). Bei Bell-Zahlen gibt es keinen führenden Term.")
st.dataframe(error_rows(a), hide_index=True, width="stretch")

if st.button("📄 PDF der aktuellen Aufgabe erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, build_pdf(a))
made = st.session_state.get("pdf_made")
if made and made[0] == settings:
    st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="asymptotik.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie schnell wächst die Zahl, und wie gut ist die Näherung?")
verdict(verdict_answers(a))

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Dieselben Zahlen auf allen Wegen")
st.caption(f"Der exakte Koeffizient auf zwei unabhängigen Wegen (Formel oder Rekursion gegen die Gleichung, das Teilen durch den Nenner, den Kalkül aus Stück 6 bis n = {C.EGF_CHECK_N}, das Aufzählen kanonischer Formen bis n = {C.ENUM_TREE_N}); "
           "bei Catalan und Motzkin zusätzlich Lage und Amplitude aus dem System gegen die geschlossene Form.")
if a.problems:
    st.error("Die Rechenwege widersprechen sich: " + "; ".join(a.problems))
else:
    st.success("Alle gerechneten Wege geben dieselbe Zahl.")
st.dataframe(way_rows(a), hide_index=True, width="stretch")

st.markdown("---")

st.subheader("🔬 Experiment 2: Der Transfersatz")
st.caption("Der exakte Koeffizient von (1 − z)^(−a) gegen n^(a−1)/Γ(a): der Fehler ist a(a−1)/(2n) plus Glieder höherer Ordnung. a = −1/2 ist der Wurzelfall, a = 1 die geometrische Reihe (exakt), a = 2 und 3 sind Pole.")
transfer = _transfer()
st.plotly_chart(build_transfer(transfer), width="stretch", key="transfer_chart")
st.dataframe([{"a": f"{r['a']:g}", "n": r["n"], "Fehler": sci_text(r["Fehler"], 3), "n mal Fehler": de(r["n·Fehler"], 4), "a(a−1)/2": de(r["a(a−1)/2"], 4)} for r in transfer], hide_index=True, width="stretch")
verdict(verdict_transfer(transfer))

st.markdown("---")

st.subheader("🔬 Experiment 3: Quotient gegen Richardson")
st.caption("Fehler der geschätzten Wachstumsrate: der einfache Quotient c(n+1)/c(n) gegen μ̂ = (n+1)·r(n+1) − n·r(n). Bei den Wurzelbäumen ohne Reihenfolge gibt es keinen bekannten Wert; Bezug ist die Richardson-Schätzung bei n = "
           f"{C.QUOTIENT_TREE_REF}.")
quo = _quotient()
st.plotly_chart(build_quotient(quo["rows"]), width="stretch", key="quotient_chart")
st.dataframe([{"Folge": r["Folge"], "n": r["n"], "Fehler des einfachen Quotienten": sci_text(r["einfacher Quotient"], 3), "Fehler nach Richardson": sci_text(r["Richardson"], 3)} for r in quo["rows"]], hide_index=True, width="stretch")
verdict(verdict_quotient(quo))

st.markdown("---")

st.subheader("🔬 Experiment 4: Von der Gleichung zur Konstanten")
st.caption(f"{C.SPEC_COUNT} zufällige Gleichungen F = 1 + Σ c·zʲ·Fᵏ (feste Seeds, Stück 3): Lage ρ, Gipfelwert τ und Amplitude γ kommen aus dem System, der führende Term γ/(2√π)·ρ⁻ⁿ·n^(−3/2) wird gegen die exakten Koeffizienten gestellt.")
specs = _specs()
st.plotly_chart(build_spec_errors(specs), width="stretch", key="spec_chart")
st.dataframe([{"n": r["n"], "mittlerer Fehler": de(100 * r["mittlerer Fehler"], 3) + " %", "größter Fehler": de(100 * r["größter Fehler"], 3) + " %", "mittleres n mal Fehler": de(r["mittleres n·Fehler"], 3),
               "Bereich n mal Fehler": f"{de(r['kleinstes n·Fehler'], 2)} bis {de(r['größtes n·Fehler'], 2)}"} for r in specs["rows"]], hide_index=True, width="stretch")
with st.expander("Die Gleichungen ansehen"):
    st.dataframe([{"Nr.": i + 1, "Terme (c, j, k)": ", ".join(f"{c}·z^{j}·F^{k}" for c, j, k in sp["terms"]), "ρ": de(sp["rho"], 6), "τ": de(sp["tau"], 6), "γ": de(sp["gamma"], 6)} for i, sp in enumerate(specs["specs"])],
                 hide_index=True, width="stretch")
verdict(verdict_spec(specs))

st.markdown("---")

st.subheader("🔬 Experiment 5: Wachstumsklassen und falscher Exponent")
st.caption("Der Quotient c(n+1)/c(n) verrät die Klasse. Darunter: Catalan, Konstante bei n = 100 angepasst und mit verschiedenen Exponenten bis n = 1000 fortgeschrieben.")
classes, wrong = _classes()
st.plotly_chart(build_classes(classes), width="stretch", key="classes_chart")
cols = [f"n = {n}" for n in C.CLASS_NS]
st.dataframe([{"Folge": r["Folge"], **{k: de(r[k], 4) for k in cols}} for r in classes], hide_index=True, width="stretch")
verdict(class_verdict(classes))
st.dataframe([{"Exponent": de(r["Exponent"], 1), "Vorhersage / exakt (n = 1000)": de(r["Vorhersage / exakt"], 4)} for r in wrong], hide_index=True, width="stretch")
verdict(verdict_wrong(wrong))

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🎲 Spielwiese: Die eigene Gleichung")
st.caption("F = 1 + c₁·z·F + c₂·z·F² + c₃·z²·F²: Koeffizienten wählen, ρ, τ und γ aus dem System ablesen und den führenden Term gegen die exakten Koeffizienten prüfen. Mit c₂ = c₃ = 0 ist die Gleichung linear (Pol statt Wurzel).")
q1, q2, q3, q4 = st.columns(4)
c1 = q1.slider("c₁ (z·F)", 0, C.PLAY_C_MAX, 0, key="play_c1", help="Koeffizient des Terms z·F (linear).")
c2 = q2.slider("c₂ (z·F²)", 0, C.PLAY_C_MAX, 1, key="play_c2", help="Koeffizient des Terms z·F²: Catalan-Bäume bei c₂ = 1.")
c3 = q3.slider("c₃ (z²·F²)", 0, C.PLAY_C_MAX, 0, key="play_c3", help="Koeffizient des Terms z²·F².")
pn = q4.slider("n", C.PLAY_N_MIN, C.PLAY_N_MAX, C.PLAY_N_DEFAULT, key="play_n", help="Index, bei dem die Näherung geprüft wird.")
play = _play(int(c1), int(c2), int(c3), int(pn))
if play["kind"] in ("root", "pole"):
    st.plotly_chart(build_play(play["seq"], play["n"], play["mu"]), width="stretch", key="play_chart")
verdict(verdict_play(play))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Nächste Singularität vom Wurzel- oder Poltyp** | Bei ganzen Funktionen (Bell-Zahlen) und wesentlichen Singularitäten (Partitionen) gibt es keine Rate; der Quotient wächst beziehungsweise fällt gegen 1 (Experiment 5). Sattelpunkt- und Kreismethode sind eigene Verfahren. | – |
| **Es gibt genau eine dominante Singularität** | Perioden (zum Beispiel nur gerade Größen) haben mehrere Singularitäten auf dem Rand; der Quotient ist dann 0 und die Näherung gilt nur mit Schritt p (Stück 3). Die Spielwiese meldet das. | Stück 3 |
| **Der Exponent stimmt** | Mit dem falschen Exponent liegt die Vorhersage um den Faktor 10 oder mehr daneben (Experiment 5). Die App kennt −3/2 (Wurzel), −1/2 (Wurzel im Nenner) und m − 1 (Pol). | – |
| **Die Konstante ist aus dem System ablesbar** | Bei den Wurzelbäumen ohne Reihenfolge ist die Gleichung nicht algebraisch: die Konstante wird angepasst (bei n/2), nicht berechnet. | – |
| **Der Fehler fällt wie 1/n** | Gemessen bis n = {C.N_MAX}; die Konstante B des nächsten Terms ist bei Catalan, Motzkin, zentralem Binomialkoeffizienten und beschrifteten Bäumen bekannt, sonst nicht. | – |
| **Gleitkomma genügt** | Die Logarithmen großer Zahlen sind auf etwa 15 Stellen genau; Fehler unter 10⁻¹⁵ sind Rundung. Die exakten Zahlen selbst sind ganz oder Brüche. | – |
| **Die Größe ist begrenzt** | Wurzelbäume ohne Reihenfolge bis n = {C.N_CAP['Wurzelbäume ohne Reihenfolge']}, die eigene Gleichung bis n = {C.PLAY_N_MAX}, sonst bis n = {C.N_MAX}; darüber wird gekappt und das gesagt. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Wachstumsrate und Exponent.** Hat die erzeugende Funktion $F(z) = \sum c_n z^n$ mit nichtnegativen Koeffizienten die nächste Singularität bei $\rho > 0$, so wächst $c_n$ wie $\rho^{-n}$ (bis auf subexponentielle Faktoren), und es gilt $c_n \approx A\, \rho^{-n} n^{\alpha}$ mit dem Exponenten $\alpha$ der Singularität.

**Transfersatz.** $[z^n]\,(1 - z/\rho)^{-a} = \rho^{-n}\, \dfrac{\Gamma(n+a)}{\Gamma(n+1)\,\Gamma(a)} = \rho^{-n}\, \dfrac{n^{a-1}}{\Gamma(a)} \Big(1 + \dfrac{a(a-1)}{2n} + O(n^{-2})\Big)$. Für $a = -\tfrac12$ (Wurzel) ist $\Gamma(-\tfrac12) = -2\sqrt{\pi}$ und der Koeffizient von $-\sqrt{1 - z/\rho}$ ist $\dfrac{\rho^{-n}}{2\sqrt{\pi}\, n^{3/2}}$.

**Wurzelsingularität bei einer Gleichung.** Für $F = \Phi(z, F)$ mit nichtnegativen Koeffizienten, nichtlinear in $F$ und aperiodisch, sind $(\rho, \tau)$ die Lösung von $\tau = \Phi(\rho, \tau)$, $\Phi_y(\rho, \tau) = 1$, und nahe $\rho$ gilt
$$F(z) = \tau - \gamma \sqrt{1 - z/\rho} + O(1 - z/\rho), \qquad \gamma = \sqrt{\frac{2\rho\, \Phi_z(\rho, \tau)}{\Phi_{yy}(\rho, \tau)}}, \qquad c_n \sim \frac{\gamma}{2\sqrt{\pi}}\, \rho^{-n} n^{-3/2}.$$
Catalan ($F = 1 + zF^2$): $\rho = \tfrac14$, $\tau = 2$, $\gamma = 2$, $c_n \sim 4^n / (\sqrt{\pi}\, n^{3/2})$, exakt $c_n = \frac{4^n}{\sqrt{\pi}\, n^{3/2}} \big(1 - \tfrac{9}{8n} + \dots\big)$.

**Pol.** Für $F = (1 - z/\rho)^{-m} G(z)$ mit $G$ regulär bei $\rho$ gilt $c_n \sim G(\rho)\, \dfrac{n^{m-1}}{\Gamma(m)}\, \rho^{-n}$; bei $1/(1 - z - z^2)^m$ ist $G(\rho) = (1 + \varphi^{-2})^{-m}$.

**Quotient und Richardson.** Aus $c_n \approx K \mu^n n^{\alpha}$ folgt $r_n = c_{n+1}/c_n = \mu\,(1 + \alpha/n + b/n^2 + \dots)$. Der Fehler $r_n - \mu$ fällt wie $1/n$; die Kombination $\hat\mu_n = (n+1)\, r_{n+1} - n\, r_n = \mu + O(n^{-2})$ beseitigt den $1/n$-Term. Der Exponent folgt aus $\hat\alpha = n\,(r_n / \mu - 1)$.

**Hardy–Ramanujan.** $p(n) \sim \dfrac{1}{4 n \sqrt{3}}\, e^{\pi \sqrt{2n/3}}$; der Quotient $p(n+1)/p(n)$ strebt gegen 1, weil die Singularität bei $z = 1$ wesentlich ist.

**Literatur** (Titel und Fundstelle aus dem Gedächtnis, nicht eingesehen).
P. Flajolet und R. Sedgewick: *Analytic Combinatorics*, Cambridge University Press, 2009 (Transfersätze, Singularitätenanalyse, Wurzel- und Polfälle).
P. Flajolet und A. Odlyzko: *Singularity analysis of generating functions*, SIAM Journal on Discrete Mathematics 3 (2), 1990, S. 216–240.
G. H. Hardy und S. Ramanujan: *Asymptotic formulae in combinatory analysis*, Proceedings of the London Mathematical Society 17, 1918, S. 75–115.
R. Otter: *The number of trees*, Annals of Mathematics 49, 1948, S. 583–599 (Wurzelbäume ohne Reihenfolge, Wachstumskonstante 2,9557…).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
