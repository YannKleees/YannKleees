import csv
import io
from pathlib import Path

import numpy as np
import requests

from theme import MONO, SANS, THEMES, svg, text, write

ROOT = Path(__file__).resolve().parent.parent
RESULTS = "https://raw.githubusercontent.com/YannKleees/hyperreimpute/main/results"
TAGLINE = "Data scientist. MSc Applied Data Science, Utrecht University. Based in Luxembourg."
METHODS = {
    "mean": "Mean",
    "ice_lr": "ICE, linear",
    "ice_rf": "ICE, random forest",
    "column_naive_paper": "Column-naive (paper)",
    "hyperimpute": "HyperImpute",
    "ice_cb_fixed": "ICE, tuned CatBoost",
}
DATASETS = ["airfoil", "compression", "wine_white"]


def header(theme):
    t = THEMES[theme]
    body = [
        f'<rect x="0" y="6" width="32" height="3" fill="{t["accent"]}"/>',
        text(0, 74, "Yann Klees", 52, t["ink"], SANS, 650, extra=' letter-spacing="-1"'),
        text(0, 112, TAGLINE, 17, t["secondary"], SANS),
    ]
    return svg(880, 128, f"Yann Klees. {TAGLINE}", "\n".join(body))


def rmse():
    rows = []
    for f in ["main.csv", "ice_cb_fixed.csv", "ablation_extra.csv"]:
        s = requests.get(f"{RESULTS}/{f}", timeout=30).text
        rows += [r for r in csv.DictReader(io.StringIO(s)) if r["mechanism"] == "MAR"]
    out = {}
    for d in DATASETS:
        for m in METHODS:
            x = np.array([float(r["rmse"]) for r in rows if r["dataset"] == d and r["method"] == m])
            out[d, m] = (x.mean(), x.std(ddof=1), len(x))
    return out


def at(v, x0, hi, panel):
    return x0 + v / hi * panel


def thumbnail(stats, theme):
    t = THEMES[theme]
    w, h, left, top, row = 600, 268, 150, 44, 26
    panel, gap = 136, 14
    color = {"hyperimpute": t["ink"], "ice_cb_fixed": t["accent"]}
    body = []
    for i, m in enumerate(METHODS):
        y = top + 14 + i * row
        strong = m in color
        body.append(
            text(
                left - 14,
                y + 4,
                METHODS[m],
                12,
                t["ink"] if strong else t["secondary"],
                SANS,
                600 if strong else 400,
                "end",
            )
        )
    for k, d in enumerate(DATASETS):
        x0 = left + k * (panel + gap)
        top_value = max(stats[d, m][0] + stats[d, m][1] for m in METHODS)
        hi = np.ceil(top_value * 20) / 20
        bottom = top + len(METHODS) * row
        body += [
            text(x0, top - 14, d, 12, t["ink"], MONO, 500),
            f'<line x1="{x0}" y1="{top}" x2="{x0}" y2="{bottom}" stroke="{t["rule"]}"/>',
            f'<line x1="{x0}" y1="{bottom}" x2="{x0 + panel}" y2="{bottom}" stroke="{t["rule"]}"/>',
            text(x0, bottom + 16, "0", 10, t["muted"], MONO),
            text(x0 + panel, bottom + 16, f"{hi:.2f}", 10, t["muted"], MONO, anchor="end"),
        ]
        for i, m in enumerate(METHODS):
            y = top + 14 + i * row
            mean, sd, _ = stats[d, m]
            fill = color.get(m, t["muted"])
            body += [
                f'<line x1="{at(max(mean - sd, 0), x0, hi, panel):.1f}" y1="{y}" x2="{at(mean + sd, x0, hi, panel):.1f}" y2="{y}" stroke="{fill}" stroke-width="2" stroke-linecap="round" opacity=".35"/>',
                f'<circle cx="{at(mean, x0, hi, panel):.1f}" cy="{y}" r="4.5" fill="{fill}"/>',
            ]
    body.append(
        text(0, h - 8, "RMSE, mean and ±1 sd over 10 seeds, MAR missingness. Lower is better.", 11, t["muted"], MONO)
    )
    summary = "; ".join(
        f"{d}: HyperImpute {stats[d, 'hyperimpute'][0]:.3f}, tuned CatBoost {stats[d, 'ice_cb_fixed'][0]:.3f}"
        for d in DATASETS
    )
    return svg(w, h, f"Imputation RMSE by method and dataset. {summary}.", "\n".join(body))


def main():
    stats = rmse()
    for theme in THEMES:
        write(ROOT / "assets" / f"header_{theme}.svg", header(theme))
        write(ROOT / "assets" / f"hyperreimpute_{theme}.svg", thumbnail(stats, theme))
    for d in DATASETS:
        a, b = stats[d, "hyperimpute"][0], stats[d, "ice_cb_fixed"][0]
        print(
            f"{d:12} hyperimpute={a:.4f} ice_cb_fixed={b:.4f} lower by {100 * (a - b) / a:.1f}% (n={stats[d, 'hyperimpute'][2]})"
        )


if __name__ == "__main__":
    main()
