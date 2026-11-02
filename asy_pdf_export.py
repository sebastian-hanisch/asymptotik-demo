"""PDF-Export der aktuellen Aufgabe mit den Rechenwegen und den ersten Werten (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

from asy_evaluation import Analysis, error_rows, verdict_answers, way_rows

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "€": "EUR", "„": '"', "“": '"', "ⁿ": "^n", "²": "^2", "ₖ": "k", "∞": "unendlich",
            "⁻": "-", "⁰": "0", "¹": "1", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "ₙ": "n"}


def _s(text) -> str:
    out = str(text)
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(a: Analysis) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Asymptotik: Lage und Art der Singularität"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    extra = f", Vielfachheit {a.settings.m}" if a.settings.family == "Fibonacci-Pole" else ""
    pdf.multi_cell(0, 5, _s(f"{a.settings.family}{extra}, n = {a.n_eff}. Alles gerechnet, keine Messdaten."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.multi_cell(0, 5, _s(verdict_answers(a)[1]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    widths = (45, 70, 55, 20)
    heads = ("Frage", "Weg", "Ergebnis", "Prüfung")
    for h, w in zip(heads, widths):
        pdf.cell(w, 6, _s(h), border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 8)
    for row in way_rows(a):
        for key, w in zip(heads, widths):
            pdf.cell(w, 5.5, _s(row[key])[:42], border=1)
        pdf.ln()
    pdf.ln(3)
    rows = error_rows(a)
    keys = list(rows[0])
    pdf.set_font("Helvetica", "B", 9)
    for k in keys:
        pdf.cell(45, 6, _s(k)[:24], border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for row in rows:
        for k in keys:
            pdf.cell(45, 5.5, _s(row[k])[:24], border=1)
        pdf.ln()
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s("Quelle: asymptotik-demo, Sebastian Hanisch."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
