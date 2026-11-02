# Asymptotik – Lage und Art der Singularität – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-asymptotik-demo.streamlit.app/)** -->

Stück 9 von 16 der Reihe **„Abzählen und erzeugende Funktionen“** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (die Linie wird erst vollständig veröffentlicht). Vorgänger sind `aufzaehlen-rekursion-demo` (Stück 1), `rationale-ef-demo` (Stück 2), `symbolische-methode-demo` (Stück 3), `semiring-rekursion-demo` (Stück 4), `multimengen-partitionen-demo` (Stück 5), `beschriftete-strukturen-demo` (Stück 6), `siebformel-demo` (Stück 7) und `zaehlen-nach-parameter-demo` (Stück 8); sie haben **exakte Zahlen** geliefert. Diese Demo fragt, **wie schnell diese Zahlen wachsen** und **wie gut eine Näherung ist**: Die **nächste Singularität** ρ der erzeugenden Funktion bestimmt die **Wachstumsrate** 1/ρ, ihre **Art** (Wurzel oder Pol) den **polynomiellen Faktor**, und das Gleichungssystem aus Stück 3 liefert die **Konstante**. Der **Transfersatz** macht daraus c(n) ≈ γ/(2√π)·ρ⁻ⁿ·n^(−3/2); der Fehler fällt wie 1/n und wird gemessen. Der Quotient c(n+1)/c(n) ist eine schlechte Schätzung der Rate; die **Richardson-Extrapolation** verbessert sie um eine Ordnung. Bei den Bell-Zahlen und den Partitionen gibt es **keine Rate**, und die Demo zeigt, woran man das sieht.

## Warum dieses Problem

Wer plant, muss wissen, ob ein Verfahren, das alle Möglichkeiten durchgeht, bei n = 100 noch rechenbar ist, und wie viele Möglichkeiten es bei n = 1000 sind. Die exakte Zahl ist nach Stück 1 bis 8 oft schon da; ihre **Größenordnung** und der **Fehler einer Faustformel** sind es nicht. Die Demo zeigt die Rechnung (Singularität, Art, Konstante), prüft die Formel gegen die exakten Zahlen und zeigt, wo sie nicht greift.

## Befunde und Korrekturen gegenüber dem Plan

- **Hook bestätigt:** Catalan-Zahl C₁₀₀ gegen 4ⁿ/(√π·n^(3/2)): der Näherungsfehler ist 9/(8n) = 1,1263 % (n mal Fehler 1,1263 → 1,125); mit dem Korrekturfaktor (1 + B/n), B = −9/8, bleiben −0,011 %.
- **Die Korrekturkonstante wird gemessen, nicht bewiesen:** B = −9/8 (Catalan), −39/16 (Motzkin), −1/8 (zentraler Binomialkoeffizient), −1/12 (beschriftete Wurzelbäume) stehen als Werte aus dem Gedächtnis (Literatur nicht eingesehen) im Code und werden von der Messung n·Fehler (1,1251 / 2,4412 / 0,1250 / 0,0833 bei n = 1000 beziehungsweise 200) bestätigt.
- **Behauptung im Preset-Text korrigiert:** Der erste Entwurf des Standard-Presets sagte „unter 0,01 %“. Gemessen sind **0,01134 %**; der Text sagt jetzt „bei 0,011 %“. Der Test `test_preset_help_claims` hält das fest.
- **Quotient allein ist schlecht, Richardson viel besser:** Catalan n = 100: Quotient 3,9412 (Fehler 0,0588), Richardson 3,9989 (Fehler 1,1·10⁻³); beim Verdoppeln von n sinkt der Fehler des Quotienten um den Faktor 1,96 bis 1,99 (Ordnung 1), der Richardson-Schätzung um 3,81 bis 3,95 (Ordnung 2).
- **Wurzelbäume ohne Reihenfolge (Otter):** keine algebraische Gleichung; die Wachstumskonstante wird aus den Zahlen geschätzt (Richardson bei n = 600: 2,9558, Exponent −1,4941) und die Konstante K bei n/2 angepasst, nicht berechnet. Das sagt die Antwort der App.
- **Entartete Eingaben der Spielwiese:** F = 1 + z²·F² (nur Terme mit z²) ist periodisch (Periode 2), der Quotient c(n+1)/c(n) ist dort 0; die App meldet das, rechnet aber nicht weiter. Mit c₂ = c₃ = 0 ist die Gleichung linear (Pol statt Wurzel).
- **Grenzen sind kein Fehler der Rechnung:** Bell-Zahlen (ganze Funktion) und Partitionen (wesentliche Singularität) haben keine Rate: der Quotient wächst (107,07 bei n = 500, etwa das 1,33-fache von n/ln n) beziehungsweise fällt gegen 1 (1,0403 bei n = 1000).
- **Präfix:** `asy_`, Port 9322 wie geplant.
- **Eigene Fehler im Entwurf (nicht im Code):** In der ersten Fassung des Phase-0-Skripts hatte ich das Vorzeichen des Exponenten für negative a vertauscht; das Richardson-Verfahren hat bei zu kurzer Folge einen Indexfehler geworfen (jetzt +2 Reserve); eine Gleitkommazahl lief beim Diagramm über (jetzt Ganzzahldivision). Alle drei sind behoben und getestet.

## Modell

Eine Folge ist eine Liste `c[0..n]` exakter ganzer Zahlen (bei beschrifteten Bäumen Brüche: Koeffizient der exponentiellen erzeugenden Funktion). `asy_algorithm.py` enthält die acht Familien (Catalan, Motzkin, zentraler Binomialkoeffizient, Fibonacci-Pole der Vielfachheit 1 bis 3, Wurzelbäume ohne Reihenfolge, beschriftete Wurzelbäume, Bell-Zahlen, Partitionen) jeweils mit zweitem Rechenweg, das System τ = Φ(ρ, τ), Φ_y(ρ, τ) = 1 mit der Amplitude γ = √(2ρΦ_z/Φ_yy), den Transfersatz [zⁿ](1 − z)^(−a) = n^(a−1)/Γ(a)·(1 + a(a−1)/(2n) + …), den Quotienten r(n), die Richardson-Schätzung μ̂ = (n+1)·r(n+1) − n·r(n) und die Exponentenschätzung α̂ = n(r/μ − 1). Logarithmen großer Zahlen laufen über `ln`, damit nichts überläuft; Stellen werden über `digit_count` gezählt (Python wandelt Ganzzahlen nur bis 4300 Stellen in Text).

## Methodik

- **Rechenwege in der App** (Experiment 1): Catalan: Formel gegen die Gleichung F = 1 + z·F²; Motzkin: Rekursion gegen die Gleichung; zentraler Binomialkoeffizient: Formel gegen Rekursion; Pole: Faltung gegen Teilen durch den Nenner; Wurzelbäume: Rekursion gegen Aufzählen kanonischer Formen (bis n = 10); beschriftete Bäume und Bell: Formel beziehungsweise Bell-Dreieck gegen den exp-Kalkül aus Stück 6 (bis n = 150); Partitionen: Fünfeckszahlen gegen das Produkt. Bei Catalan und Motzkin zusätzlich Lage und Amplitude aus dem System gegen die geschlossene Form. Bei Abweichung zeigt die App einen Fehler.
- **Eingabe:** Familie, Größe n (10 bis 1000, Wurzelbäume bis 600), Vielfachheit m (nur Pole). Die Adresszeile spiegelt die Einstellung.
- **Fünf Experimente:** (1) alle Wege, (2) Transfersatz für a = 0,5, −0,5, 1,5, 2, 3, (3) Quotient gegen Richardson, (4) 24 zufällige Gleichungen (Seed 20261101), (5) Wachstumsklassen und falscher Exponent. Dazu eine Spielwiese: F = 1 + c₁·z·F + c₂·z·F² + c₃·z²·F².

## Befunde (gemessen, keine Behauptungen)

Jede Zahl steht in `tests/test_claims.py`, `tests/test_algorithm.py`, `tests/test_verdicts.py` oder `tests/test_oracle_asy.py`. Zeiten stehen in keinem Test.

| Frage | Befund |
|---|---|
| Handinstanzen | Catalan C₁₀ = 16796 gegen 4¹⁰/(√π·10^1,5) = 18707,9 (Verhältnis 1,1138); System für F = 1 + z·F²: ρ = 1/4, τ = 2, γ = 2; 1/(1 − z − z²)² beginnt 1, 2, 5, 10, 20, 38; Richardson bei Catalan n = 3: 4·3 − 3·2,8 = 3,6 |
| Standardfall, Catalan n = 100 | c(100) = 8,96·10⁵⁶ (57 Stellen); Quotient 3,9412, Richardson 3,9989, Exponent n(r/4 − 1) = −1,4706; Näherungsfehler 1,1263 %, mit Korrektur −0,01134 % |
| Fehler des führenden Terms (Catalan), n = 10, 20, 50, 100, 200, 500, 1000 | 11,383 %, 5,658 %, 2,255 %, 1,126 %, 0,563 %, 0,225 %, 0,113 %; n mal Fehler 1,1383, 1,1316, 1,1277, 1,1263, 1,1257, 1,1253, 1,1251 (Grenzwert 9/8); mit Korrektur −1,148 %, −0,285 %, −0,045 %, −0,011 % für n = 10 bis 100 |
| Weitere Wurzelfälle | Motzkin n = 200: ρ = 1/3, Fehler 1,2206 %, n mal Fehler 2,4412 (B = −39/16 = −2,4375); zentraler Binomialkoeffizient n = 500: Exponent −1/2, n mal Fehler 0,1250; beschriftete Wurzelbäume n = 1000: ρ = 1/e, n mal Fehler 0,0833 |
| Doppelter Pol 1/(1 − z − z²)², n = 300 | Exponent 1; Näherung −0,5149 % daneben, n(r/φ − 1) = 0,9949 |
| Wurzelbäume ohne Reihenfolge | n = 400: Richardson-Rate 2,955733, Exponent −1,4912, Näherung −0,8387 % daneben; n = 600: Rate 2,9558, Exponent −1,4941; C₁₀₀₀ hat 598 Stellen, B₁₀₀₀ (Bell) hat 1928 |
| Keine Rate | Bell n = 500: Quotient 107,07, etwa 1,33·n/ln n; Partitionen n = 1000: Quotient 1,0403, Hardy–Ramanujan 1,42 % zu hoch (Fehler mal √n = 0,448); p(10) = 42 gegen 48,06 |
| Experiment 2: Transfersatz, n·Fehler bei n = 1000 | a = 0,5: −0,125; a = −0,5: 0,375; a = 1,5: 0,375; a = 2: 1,000; a = 3: 3,002 (a(a−1)/2 = −0,125 / 0,375 / 0,375 / 1 / 3); höchste Abweichung 0,0020 |
| Experiment 3: Rate Catalan, n = 50, 100, 200, 400 | Fehler des Quotienten 0,1154, 0,0588, 0,0297, 0,0149; Richardson 4,35·10⁻³, 1,14·10⁻³, 2,93·10⁻⁴, 7,41·10⁻⁵ (bei n = 400 etwa 202-mal genauer) |
| Experiment 4: 24 Zufallsgleichungen | mittlerer Fehler des führenden Terms bei n = 50, 100, 200: 2,25 %, 1,12 %, 0,56 % (größter 2,17 % bei n = 200); mittlerer Quotientenfehler bei n = 200 0,0074 (≈ 3/(2n) = 0,0075) |
| Experiment 5: Quotient bei n = 10, 100, 1000 | Catalan 3,500, 3,941, 3,994; Bell 5,9, 29,6, 190,6; Partitionen 1,333, 1,125, 1,040; n! 11, 101, 1001 |
| Falscher Exponent (Catalan, Konstante bei n = 100, Vorhersage n = 1000) | Verhältnis Vorhersage / exakt: −1,5: 0,990; −0,5: 9,9; −2,5: 0,099; 0: 31,3 |
| Spielwiese | F = 1 + z·F²: ρ = 0,25, τ = 2, γ = 2, bei n = 200 0,563 % Fehler; F = 1 + z·F + z·F² + z²·F²: ρ = 0,154701, τ = 2,366025, γ = 2,897777; F = 1 + 2z·F + 3z²·F²: ρ = 0,183013, τ = 3,154701, γ = 5,603214 |

## Ehrliche Grenzen

- **Literaturwerte aus dem Gedächtnis:** Transfersatz, Hardy–Ramanujan, Otters Wachstumskonstante 2,9557… und die Korrekturkonstanten wurden nicht an einer Quelle gelesen. Die exakten Zahlen und die Messung stützen sie, das ersetzt keine Quelle.
- **Nur Wurzel und Pol:** Bell-Zahlen (Sattelpunktmethode) und Partitionen (Kreismethode) sind eigene Verfahren; die Demo zeigt nur, dass dort der Quotient keine Rate liefert.
- **Eine dominante Singularität:** Gleichungen mit Periode (nur gerade Größen) haben mehrere Singularitäten auf dem Rand; die Spielwiese meldet das und rechnet nicht.
- **Exponent und Konstante werden vorausgesetzt:** Bei den Wurzelbäumen ohne Reihenfolge stammt −3/2 aus der Theorie, die Konstante wird angepasst.
- **Fehler gemessen bis n = 1000** (Wurzelbäume 600), nicht bewiesen; die Behauptung „fällt wie 1/n“ ist eine Messung für die gerechneten Familien.
- **Gleitkomma:** Logarithmen sind auf etwa 15 Stellen genau; Fehler unter 10⁻¹⁵ sind Rundung. Die Zahlen selbst sind exakt.
- **Zufallsgleichungen:** nur 24, mit festem Seed; das ist kein Beweis für alle Gleichungen.
- **Browser:** Seitentext, Zahlen, Diagrammbreiten, Preset-Klick im Browser geprüft; Handy-Breite nicht.
- Alles gerechnet, keine echten Daten.

## Verifikation

- **Kern:** Handinstanzen (Catalan bis C₁₀, Fibonacci-Quadrat, System für Catalan, Richardson bei n = 3, Binomialkoeffizienten von (1 − z)^(−a)), zweiter Weg für jede Folge (Binomialformel und Dyck-Zerlegung, Trinomialsumme, lineare Rekursion der Pole, Aufzählen kanonischer Bäume, Cayley und Stirling-Summe, Münzwechsel für die Partitionen), Substitution gegen Online-Rechnung für alle 64 kleinen Gleichungen, System erfüllt beide Gleichungen und stimmt mit der aus den Zahlen geschätzten Rate überein.
- **Eigenschaften:** n·Fehler konstant bei allen vier algebraischen Familien und gleich −B; Korrektur verkleinert den Fehler mindestens 50-fach; Richardson schlägt den Quotienten; Polexponent m − 1; Transferfehler → a(a−1)/(2n); Zufallsgleichungen haben gültige Singularitäten; Folgen wachsen monoton; alle Familien auf allen Stützstellen ohne Widerspruch der Rechenwege.
- **Randfälle:** Größen unter und über den Grenzen, Kappung je Familie mit Hinweis, unbekannte Familie, Zahlen über 4300 Stellen nur formatiert, Spielwiese mit allen 64 Koeffizientenkombinationen (trivial, periodisch, linear, Wurzel), Formatierung.
- **Urteilstexte:** genauer Wortlaut für die Standardfälle aller Experimente.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum), jede Familie, jedes Preset, Permalink mit Müll, Spielwiese, PDF, eindeutige Diagrammschlüssel; Footer-Test; Layout-Test.
- **Nicht gemacht:** Mutationstests (seit 2026-10-28 nicht mehr verlangt), Docker-Lauf der Linux-CI (Docker fehlt auf diesem Rechner; die CI nach dem Push entscheidet).

122 Tests (`pytest tests`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Kernfrage, fünf Experimente, Spielwiese, Grenzen, Formeln |
| `asy_algorithm.py` | Kern: Folgen, System, Amplitude, Transfersatz, Quotient, Richardson |
| `asy_constants.py` | Regler-Grenzen, Experiment-Konstanten, Farben, Presets |
| `asy_evaluation.py` | Analyse, Experimente, Urteilstexte, Formatierung |
| `asy_layout.py` | Fester Kopf (Stylesheet) |
| `asy_pdf_export.py` | PDF der aktuellen Aufgabe (fpdf2) |
| `asy_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben) |
| `asy_scenario.py` | Familie aus der Auswahl: Art, Exponent, Lage, Amplitude, Korrektur, Kappung |
| `asy_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handwerte, Orakel, Eigenschaften, Randfälle, Urteilstexte, Claims, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Sattelpunktmethode (Bell), Kreismethode (Partitionen), mehrere dominante Singularitäten, logarithmische Singularitäten:** eigene Verfahren; hier nur die Abgrenzung.
- **Beweis des Transfersatzes:** Die Demo misst den Fehler und rechnet die Konstante aus dem System; der Beweis (Flajolet und Odlyzko) steht nicht darin.
- **Gleichverteilt ziehen aus der Familie:** Stück 10.
- **Symmetrien und Polynome (Burnside, Tutte):** Stück 11 bis 14.
- **Verwandte Demos:** `symbolische-methode-demo` (System und Wurzelsingularität), `rationale-ef-demo` (Pole), `multimengen-partitionen-demo` (Partitionen, Bäume ohne Reihenfolge), `beschriftete-strukturen-demo` (exp-Kalkül); nur Verweise.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud: Python-Version nach der Voreinstellung der Plattform (lokal `3.14`, CI `3.12`); der Code nutzt nur Merkmale, die in `3.12` laufen.

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
