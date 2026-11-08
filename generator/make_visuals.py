"""Draw a simple "how it works" flow for each project and the link buttons, in light and dark versions.

    python generator/make_visuals.py

Writes assets/flow/<project>_<theme>.svg and assets/buttons/<name>_<theme>.svg.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

THEMES = {
    "light": dict(panel="#f6f8fa", border="#d8dee4", text="#1f2328", dim="#656d76", accent="#0969da"),
    "dark": dict(panel="#161b22", border="#30363d", text="#e6edf3", dim="#8d96a0", accent="#4493f8"),
}

# Each step is (name, what it does); a list of steps runs side by side.
FLOWS = {
    "tagging": [("Input", "LU, FR, DE, EN text"), ("Rules", "Rust, gazetteers"),
                ("Model", "GLiNER, context"), ("Merge", "resolves overlaps"),
                ("Output", "placeholders")],
    "pii-anonymisation-thesis": [("Generate", "synthetic DOCX, PDF"), ("Zone", "cover pages, tables"),
                                 ("Detect", "regex, GLiNER, OCR"), ("Redact", "true removal"),
                                 ("Attack", "re-identification")],
    "orthodontic-par": [("Capture", "5 intraoral photos"), ("Detect", "YOLO11s, 10 classes"),
                        ("Map", "findings to PAR"), ("Review", "clinician edits"),
                        ("Report", "PAR over visits")],
    "job-recommender": [[("Candidate", "encoder tower"), ("Job", "encoder tower")], ("Embed", "shared vector space"),
                        ("Retrieve", "nearest neighbours"), ("Rank", "top-k per candidate")],
    "hyperreimpute": [("Data", "3 UCI datasets"), ("Mask", "MCAR, MAR, MNAR"), ("Impute", "HyperImpute"),
                      ("Compare", "vs fixed CatBoost"), ("Test", "RMSE, paired tests")],
    "music-mystery": [("Play", "30 s Deezer snippet"), ("Guess", "artist, title, year"), ("Rate", "Elo per mode"),
                      ("Adapt", "hints, snippet length")],
    "pizza-ordering-system": [("Order", "customer app"), ("Store", "MySQL, 16 tables"), ("Prepare", "staff app"),
                              ("Deliver", "by postal area"), ("Report", "earnings")],
    "record": [("Listen", "any media player"), ("Read", "track info from Windows"), ("Split", "at the silence"),
               ("Save", "tagged MP3 or FLAC")],
    "wichtel": [("Add", "three or more names"), ("Draw", "one gift circle"), ("Share", "one link per person"),
                ("Reveal", "own match only")],
    "r-projects": [("Data", "students, IMDB reviews"), ("Represent", "features, TF-IDF"),
                   ("Model", "RF, KNN, GMM, LDA"), ("Evaluate", "CV, silhouette, purity")],
    "datapluck": [("Select", "table, chart or PDF"), ("Extract", "DOM, chart data, pixels"),
                  ("Preview", "typed columns"), ("Export", "CSV, LaTeX, pandas, R")],
}

W, GAP, BOX_H, STACK_GAP = 880, 28, 72, 8


def step(x, y, w, h, num, name, detail, t):
    mid = y + h / 2
    return (f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{w - 1}" height="{h - 1}" rx="10" fill="{t["panel"]}" stroke="{t["border"]}"/>'
            f'<text x="{x + 14}" y="{mid - 5}" font-size="11" font-weight="600" fill="{t["accent"]}">{num:02d}</text>'
            f'<text x="{x + 36}" y="{mid - 5}" font-size="14.5" font-weight="600" fill="{t["text"]}">{escape(name)}</text>'
            f'<text x="{x + 14}" y="{mid + 15}" font-size="12.5" fill="{t["dim"]}">{escape(detail)}</text>')


def flow(steps, t):
    n = len(steps)
    stacked = any(isinstance(s, list) for s in steps)
    height = 2 * BOX_H + STACK_GAP if stacked else BOX_H
    bw = (W - (n - 1) * GAP) / n
    parts, num = [], 1
    for i, s in enumerate(steps):
        x = i * (bw + GAP)
        group = s if isinstance(s, list) else [s]
        h = (height - STACK_GAP * (len(group) - 1)) / len(group) if len(group) > 1 else BOX_H
        y = 0 if len(group) > 1 else (height - BOX_H) / 2
        for name, detail in group:
            parts.append(step(x, y, bw, h, num, name, detail, t))
            y += h + STACK_GAP
            num += 1
        if i < n - 1:
            ax, cy = x + bw + 7, height / 2
            parts.append(f'<path d="M{ax} {cy} h{GAP - 14} m-5 -4 l5 4 l-5 4" fill="none" stroke="{t["dim"]}" '
                         f'stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" '
            f'font-family="{SANS}">\n{"".join(parts)}\n</svg>\n')


ICONS = {
    "linkedin": '<path transform="translate({x},{y}) scale(0.58)" fill="{c}" d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.850 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.140 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>',
    "mail": '<g transform="translate({x},{y})" fill="none" stroke="{c}" stroke-width="1.5"><rect x="0.75" y="1.75" width="12.5" height="10.5" rx="2"/><path d="M1.5 3.5l5.5 4.2 5.5-4.2"/></g>',
    "repo": '<g transform="translate({x},{y})" fill="none" stroke="{c}" stroke-width="1.5" stroke-linejoin="round"><path d="M1 2.5h4l1.4 1.7H13v7.8H1z"/></g>',
}


def button(label, icon, t):
    wide, narrow = set("mwMW@%"), set("ijlrtf.,:;!|' -")
    w = int(sum(10.5 if c in wide else 4.2 if c in narrow else 7.0 for c in label) + 66)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="32" viewBox="0 0 {w} 32" font-family="{SANS}">
<rect x="0.5" y="0.5" width="{w - 1}" height="31" rx="8" fill="{t["panel"]}" stroke="{t["border"]}"/>
{ICONS[icon].format(x=13, y=9, c=t["text"])}
<text x="35" y="20.5" font-size="13" font-weight="500" fill="{t["text"]}">{escape(label)}</text>
<text x="{w - 16}" y="20.5" font-size="12" text-anchor="middle" fill="{t["dim"]}">↗</text>
</svg>
'''


BUTTONS = {"linkedin": ("LinkedIn", "linkedin"), "email": ("yannklees@gmail.com", "mail"),
           "repo": ("View repository", "repo")}


def main():
    for folder in ("flow", "buttons"):
        (ROOT / "assets" / folder).mkdir(parents=True, exist_ok=True)
    for theme, t in THEMES.items():
        for name, steps in FLOWS.items():
            (ROOT / "assets" / "flow" / f"{name}_{theme}.svg").write_text(flow(steps, t), encoding="utf-8")
        for name, (label, icon) in BUTTONS.items():
            (ROOT / "assets" / "buttons" / f"{name}_{theme}.svg").write_text(button(label, icon, t), encoding="utf-8")
    print("flows and buttons written to assets/")


if __name__ == "__main__":
    main()
