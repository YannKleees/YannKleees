"""Draw the "how it works" diagram for each project and the link buttons, in light and dark versions.

    python generator/make_visuals.py

Writes assets/diagrams/<project>_<theme>.svg and assets/links/<name>_<theme>.svg.
"""
import textwrap
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

THEMES = {
    "light": dict(bg="#ffffff", panel="#f6f8fa", border="#d0d7de", text="#1f2328", dim="#59636e",
                  accent="#0969da", accent_bg="#ddf4ff", out="#8250df", out_bg="#fbefff",
                  chip="#eaeef2", mark=["#ffebe9", "#cf222e"], mark2=["#dafbe1", "#1a7f37"]),
    "dark": dict(bg="#0d1117", panel="#161b22", border="#30363d", text="#e6edf3", dim="#8d96a0",
                 accent="#58a6ff", accent_bg="#0c2d6b", out="#d2a8ff", out_bg="#2e1a4a",
                 chip="#21262d", mark=["#5a1e24", "#ff7b72"], mark2=["#123d24", "#3fb950"]),
}

# Each stage is a box (title, detail) or a list of boxes that run side by side.
PROJECTS = {
    "tagging": dict(
        stages=[("Text", "Luxembourgish, French, German, English"),
                ("Rust rules", "patterns and gazetteers of names and places"),
                ("GLiNER model", "finds names the rules miss, from context"),
                ("Merge", "overlaps resolved, post-processing"),
                ("Redacted text", "each person keeps one placeholder")],
        example=([("De ", None), ("Jean Schmit", "PER"), (" wunnt zu ", None), ("Déifferdeng", "LOC"), (".", None)],
                 [("De ", None), ("[PER]", "PER"), (" wunnt zu ", None), ("[LOC]", "LOC"), (".", None)]),
        facts=["recall on hard Luxembourgish names: 0.57 with rules, 0.91 with the model",
               "precision 1.00", "Rust core with Python bindings"]),
    "pii-anonymisation-thesis": dict(
        stages=[("Synthetic documents", "agendas, minutes, project plans as DOCX and PDF"),
                ("Layout zones", "cover pages, headers, footers, tables"),
                ("Detection", "patterns, GLiNER, OCR, cross-region linking"),
                ("Redaction", "text removed, not just covered"),
                ("Attacker", "tries to re-identify the authors")],
        facts=["recall 0.998 on 500 documents", "text-only baseline: 44% of mentions",
               "attacker signals per document: 17.3 before, 0.16 after"]),
    "orthodontic-par": dict(
        stages=[("5 photos", "upper, lower, left, right, front"),
                ("Mosaic", "one 3x2 image per visit"),
                ("YOLO11s", "detects 10 kinds of findings"),
                ("PAR suggestions", "overjet and crowding boxes, score 1"),
                ("Clinician", "moves, grades or deletes boxes"),
                ("PDF report", "PAR score over all visits")],
        facts=["mAP50 0.697 on the OMNI test set (paper's best: 0.664)",
               "beats a Faster R-CNN under the same evaluation (0.653 vs 0.627)", "trained on a free Kaggle GPU"]),
    "job-recommender": dict(
        stages=[[("Candidate tower", "profile to embedding"), ("Job tower", "vacancy to embedding")],
                ("Shared space", "candidates and jobs side by side"),
                ("Retrieval", "nearest jobs, plus item-to-item: similar jobs"),
                ("Top-k jobs", "ranked list per candidate")],
        facts=["modular pipeline: retrieval steps can be swapped", "group project, I built most of the engine",
               "private: trained on client data"]),
    "hyperreimpute": dict(
        stages=[("3 UCI datasets", "airfoil, compression, white wine"),
                ("Remove values", "MCAR, MAR and MNAR patterns"),
                ("HyperImpute", "picks a model per column automatically"),
                ("Baselines", "including CatBoost with fixed settings"),
                ("Compare", "error and paired tests")],
        facts=["reproduces Table 2 of the ICML 2022 paper", "version check against hyperimpute 0.1.5",
               "a fixed CatBoost baseline beat it"]),
    "music-mystery": dict(
        stages=[("Snippet", "30-second Deezer preview"),
                ("Guess", "artist, title, year, or put songs in order"),
                ("Elo rating", "one per game mode"),
                ("Adapt", "fewer hints, shorter snippets, missed songs return"),
                ("Buddy", "friendly or strict, comments and hints")],
        facts=["random and personalised versions for a user study", "release years from MusicBrainz",
               "Flask and SQLite"]),
    "pizza-ordering-system": dict(
        stages=[("Customer app", "menu, basket, discount codes"),
                ("MySQL", "16 tables: orders, menu, couriers, areas"),
                ("Staff app", "kitchen, order status, menu"),
                ("Deliveries", "grouped by postal code, couriers assigned"),
                ("Reports", "earnings with charts")],
        facts=["every 10th pizza free", "birthday discount", "prices from ingredients"]),
    "wichtel": dict(
        stages=[("Names", "three people or more"),
                ("Shuffle", "into one gift circle"),
                ("Links", "one private link per person"),
                ("Reveal", "each link shows only its own match")],
        facts=["nobody draws themselves", "no two people draw each other", "static site, no server"]),
    "record": dict(
        stages=[("Any player", "browser, VLC, Media Player"),
                ("Media controls", "title, artist and cover from Windows"),
                ("Split", "cuts at the quiet moment between tracks"),
                ("Keep complete", "skipped tracks are dropped"),
                ("Tagged file", "MP3 or FLAC with cover art")],
        facts=["collections: no track saved twice", "level meter and player controls", "Python desktop app"]),
    "datapluck": dict(
        stages=[("Click or drag", "a table, a chart or a box in a PDF"),
                ("Read", "page tables, chart libraries or pixels"),
                ("Preview", "column types and values"),
                ("Export", "CSV, Markdown, LaTeX, pandas, R")],
        facts=["SVG charts: recall 0.9998", "pie charts: 98% recognised", "runs locally in the browser"]),
}

PRIVATE = {"job-recommender", "datapluck"}
W, PAD, GAP, BOX_H = 880, 12, 26, 108


def wrap(text, width_px, size):
    return textwrap.wrap(text, max(8, int(width_px / (size * 0.56))))


def box(x, y, w, h, title, detail, t, kind):
    fill, stroke, head = {"in": (t["panel"], t["border"], t["text"]),
                          "mid": (t["accent_bg"], t["accent"], t["accent"]),
                          "out": (t["out_bg"], t["out"], t["out"])}[kind]
    dash = ' stroke-dasharray="5 4"' if kind == "in" else ""
    lines = wrap(detail, w - 12, 13)[:3]
    top = y + h / 2 - (21 + 16 * len(lines)) / 2 + 15
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="{stroke}"{dash}/>',
             f'<text x="{x + w / 2}" y="{top}" text-anchor="middle" font-size="15.5" font-weight="600" fill="{head}">{escape(title)}</text>']
    for i, line in enumerate(lines):
        parts.append(f'<text x="{x + w / 2}" y="{top + 21 + i * 16}" text-anchor="middle" font-size="13" fill="{t["dim"]}">{escape(line)}</text>')
    return "".join(parts)


def arrow(x1, y1, x2, y2, t, i):
    return (f'<path d="M{x1} {y1} C{x1 + 14} {y1} {x2 - 14} {y2} {x2 - 6} {y2}" fill="none" stroke="{t["dim"]}" '
            f'stroke-width="1.6" class="flow" style="animation-delay:{i * 0.15}s"/>'
            f'<path d="M{x2 - 7} {y2 - 4} L{x2} {y2} L{x2 - 7} {y2 + 4}" fill="none" stroke="{t["dim"]}" stroke-width="1.6"/>')


def example_row(y, example, t):
    """The tagging example: original sentence on the left, redacted one on the right."""
    def sentence(x, parts, colours):
        out, cx = [], x
        for text, tag in parts:
            w = len(text) * 9.0
            if tag:
                bg, fg = colours
                out.append(f'<rect x="{cx - 2}" y="{y - 14}" width="{w + 4}" height="22" rx="4" fill="{bg}"/>')
                out.append(f'<text x="{cx}" y="{y}" font-family="{MONO}" font-size="15" textLength="{w:.1f}" fill="{fg}">{escape(text)}</text>')
            else:
                out.append(f'<text x="{cx}" y="{y}" font-family="{MONO}" font-size="15" textLength="{w:.1f}" fill="{t["text"]}" xml:space="preserve">{escape(text)}</text>')
            cx += w
        return "".join(out), cx

    left, end = sentence(PAD + 14, example[0], t["mark"])
    mid = end + 26
    right, _ = sentence(mid + 34, example[1], t["mark2"])
    return (f'<rect x="{PAD}" y="{y - 28}" width="{W - 2 * PAD}" height="46" rx="8" fill="{t["panel"]}" stroke="{t["border"]}"/>'
            + left + f'<text x="{mid}" y="{y}" font-size="15" fill="{t["dim"]}">→</text>' + right)


def facts_row(y, facts, t):
    out, x = [], PAD
    for f in facts:
        w = len(f) * 6.6 + 28
        if x + w > W - PAD:
            x, y = PAD, y + 34
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="14" fill="{t["chip"]}"/>'
                   f'<text x="{x + w / 2}" y="{y + 19}" text-anchor="middle" font-size="13" fill="{t["text"]}">{escape(f)}</text>')
        x += w + 8
    return "".join(out), y + 28


def diagram(spec, t):
    stages = spec["stages"]
    n = len(stages)
    bw = (W - 2 * PAD - (n - 1) * GAP) / n
    y0 = 16
    parts, prev = [], None                      # prev: list of (right x, centre y) of the previous stage
    for i, st in enumerate(stages):
        x = PAD + i * (bw + GAP)
        kind = "in" if i == 0 else "out" if i == n - 1 else "mid"
        group = st if isinstance(st, list) else [st]
        h = (BOX_H - 8 * (len(group) - 1)) / len(group) if len(group) > 1 else BOX_H
        ends = []
        for j, (title, detail) in enumerate(group):
            y = y0 + j * (h + 8)
            parts.append(box(x, y, bw, h, title, detail if len(group) == 1 else detail, t, kind))
            ends.append((x + bw, y + h / 2))
        if prev:
            for k, (px, py) in enumerate(prev):
                for (_, cy) in ends:
                    parts.append(arrow(px, py, x, cy, t, i + k))
        prev = ends
    y = y0 + BOX_H + 22
    if "example" in spec:
        parts.append(example_row(y + 26, spec["example"], t))
        y += 58
    chips, bottom = facts_row(y, spec["facts"], t)
    parts.append(chips)
    h = int(bottom + 14)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" font-family="{SANS}">
<style>
.flow{{stroke-dasharray:4 5;animation:flow 1.2s linear infinite}}
@keyframes flow{{to{{stroke-dashoffset:-18}}}}
@media (prefers-reduced-motion:reduce){{.flow{{animation:none}}}}
</style>
{"".join(parts)}
</svg>
'''


# ---------------------------------------------------------------- buttons
ICONS = {
    "linkedin": '<path transform="translate({x},{y}) scale(0.67)" fill="{c}" d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>',
    "mail": '<g transform="translate({x},{y})" fill="none" stroke="{c}" stroke-width="1.7"><rect x="1" y="2.5" width="14" height="11" rx="2"/><path d="M1.5 4l6.5 5 6.5-5"/></g>',
    "repo": '<g transform="translate({x},{y})" fill="none" stroke="{c}" stroke-width="1.6"><path d="M2 3.5h4l1.5 1.8H14v7.7H2z"/></g>',
    "lock": '<g transform="translate({x},{y})" fill="none" stroke="{c}" stroke-width="1.6"><rect x="2.5" y="7" width="11" height="7.5" rx="1.5"/><path d="M5 7V5a3 3 0 0 1 6 0v2"/></g>',
}


def button(label, icon, t, primary=False):
    w = int(len(label) * 7.0 + 60)
    fg = "#ffffff" if primary else t["text"]
    bg = t["accent"] if primary else t["panel"]
    stroke = t["accent"] if primary else t["border"]
    arrow_c = fg if primary else t["dim"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="34" viewBox="0 0 {w} 34" font-family="{SANS}">
<rect x="0.5" y="0.5" width="{w - 1}" height="33" rx="17" fill="{bg}" stroke="{stroke}"/>
{ICONS[icon].format(x=14, y=9, c=fg)}
<text x="38" y="22" font-size="13.5" font-weight="600" fill="{fg}">{escape(label)}</text>
<text x="{w - 18}" y="22" font-size="14" text-anchor="middle" fill="{arrow_c}">↗</text>
</svg>
'''


def main():
    for theme, t in THEMES.items():
        d = ROOT / "assets" / "diagrams"
        d.mkdir(parents=True, exist_ok=True)
        for name, spec in PROJECTS.items():
            (d / f"{name}_{theme}.svg").write_text(diagram(spec, t), encoding="utf-8")
        links = ROOT / "assets" / "links"
        links.mkdir(parents=True, exist_ok=True)
        (links / f"linkedin_{theme}.svg").write_text(button("LinkedIn", "linkedin", t, primary=True), encoding="utf-8")
        (links / f"email_{theme}.svg").write_text(button("yannklees@gmail.com", "mail", t), encoding="utf-8")
        for name in PROJECTS:
            if name not in PRIVATE:
                (links / f"{name}_{theme}.svg").write_text(button(f"open {name}", "repo", t, primary=True),
                                                           encoding="utf-8")
    print("diagrams and buttons written to assets/")


if __name__ == "__main__":
    main()
