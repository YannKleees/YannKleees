"""Turn a photo into the profile header: a coloured ASCII portrait next to a terminal-style info panel.

    python generator/make_header.py --photo generator/photo.jpg

Steps: remove the background with rembg, crop to head and shoulders, map each cell of the photo to a
character (denser characters for brighter skin and clothes) coloured like the photo, and write
assets/header_light.svg and assets/header_dark.svg. The text on the right comes from profile.json.
"""
import argparse
import json
from html import escape
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

ROOT = Path(__file__).resolve().parent.parent
RAMP = " .:-=+*#%@"
CW, LH, FS = 4.8, 8.4, 8.0          # portrait cell width, line height and font size in px
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

THEMES = {
    "light": dict(bg="#f6f8fa", border="#d0d7de", bar="#eaeef2", text="#1f2328", dim="#59636e",
                  accent="#0969da", accent2="#8250df",
                  blocks=["#1f2328", "#cf222e", "#1a7f37", "#9a6700", "#0969da", "#8250df", "#1b7c83", "#6e7781"]),
    "dark": dict(bg="#0d1117", border="#30363d", bar="#161b22", text="#e6edf3", dim="#8d96a0",
                 accent="#58a6ff", accent2="#d2a8ff",
                 blocks=["#484f58", "#ff7b72", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#b1bac4"]),
}
DOTS = ["#ff5f57", "#febc2e", "#28c840"]


# ---------------------------------------------------------------- photo -> character grid
def cut_out(photo: Path, model: str):
    img = Image.open(photo).convert("RGB")
    img.thumbnail((1200, 1200))
    mask = remove(img, session=new_session(model), only_mask=True)
    mask = np.array(mask) > 127
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR), mask


def crop_head_and_shoulders(img, mask):
    ys, xs = np.nonzero(mask)
    top, bottom, left, right = ys.min(), ys.max(), xs.min(), xs.max()
    head = ys < top + 0.2 * (bottom - top)                  # the top fifth of the person is the head
    cx = int(xs[head].mean())
    w = int(0.8 * (right - left))
    x0 = max(0, cx - w // 2)
    x1 = min(img.shape[1], x0 + w)
    y0 = max(0, top - int(0.02 * w))
    y1 = min(img.shape[0], y0 + w)                          # roughly square
    return img[y0:y1, x0:x1], mask[y0:y1, x0:x1]


def to_grid(img, mask, cols):
    rows = round(cols * img.shape[0] / img.shape[1] * CW / LH)
    gray = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(6, 6)).apply(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    small = cv2.resize(img, (cols, rows), interpolation=cv2.INTER_AREA)
    keep = cv2.resize(mask.astype(np.uint8) * 255, (cols, rows), interpolation=cv2.INTER_AREA) >= 128
    g = cv2.resize(gray, (cols, rows), interpolation=cv2.INTER_AREA).astype(float)
    fg = np.sort(g[keep])
    g = np.searchsorted(fg, g) / len(fg)                     # equalise brightness over the person only

    grids = {}
    for theme in THEMES:
        grid = []
        for r in range(rows):
            row = []
            for c in range(cols):
                if not keep[r, c]:
                    row.append(None)
                    continue
                ch = RAMP[min(len(RAMP) - 1, 3 + int(g[r, c] * (len(RAMP) - 3)))]
                b, gr, rd = (int(v) for v in small[r, c])
                if theme == "dark":                          # lift dark colours off the dark background
                    rd, gr, b = (int(v + (255 - v) * 0.12) for v in (rd, gr, b))
                else:                                        # darker and more saturated on white
                    h, s, v = cv2.cvtColor(np.uint8([[[b, gr, rd]]]), cv2.COLOR_BGR2HSV)[0, 0].astype(int)
                    b, gr, rd = (int(x) for x in cv2.cvtColor(
                        np.uint8([[[h, min(255, int(s * 1.5)), int(v * 0.62)]]]), cv2.COLOR_HSV2BGR)[0, 0])
                row.append((ch, (rd, gr, b)))
            grid.append(row)
        grids[theme] = grid
    return grids, rows


def palette_classes(grid, k=40):
    """Snap colours to k shared ones so neighbouring characters can share one <tspan>."""
    cells = [(r, c) for r, row in enumerate(grid) for c, cell in enumerate(row) if cell]
    rgb = np.float32([grid[r][c][1] for r, c in cells])
    _, labels, centers = cv2.kmeans(rgb, k, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5),
                                    4, cv2.KMEANS_PP_CENTERS)
    out = [[None] * len(grid[0]) for _ in grid]
    for (r, c), lab in zip(cells, labels.ravel()):
        out[r][c] = (grid[r][c][0], int(lab))
    return out, ["#%02x%02x%02x" % tuple(int(v) for v in ctr) for ctr in centers]


# ---------------------------------------------------------------- SVG
def portrait_svg(grid, px, py):
    grid, palette = palette_classes(grid)
    css = "".join(f".c{i}{{fill:{p}}}" for i, p in enumerate(palette))
    lines = []
    for r, row in enumerate(grid):
        spans, c = [], 0
        while c < len(row):
            if row[c] is None:
                c += 1
                continue
            start, cls, chars = c, row[c][1], []
            while c < len(row) and row[c] is not None and row[c][1] == cls:
                chars.append(row[c][0])
                c += 1
            spans.append(f'<tspan x="{px + start * CW:.1f}" textLength="{len(chars) * CW:.1f}" '
                         f'class="c{cls}">{escape("".join(chars))}</tspan>')
        if spans:
            lines.append(f'<text class="row" y="{py + r * LH + FS:.1f}" '
                         f'style="animation-delay:{r * 28}ms">{"".join(spans)}</text>')
    return css, "\n".join(lines)


def info_svg(cfg, t, x, y, delay):
    out = [f'<text x="{x}" y="{y}" class="info title" style="animation-delay:{delay}ms">'
           f'<tspan fill="{t["accent"]}">{escape(cfg["user"])}</tspan><tspan fill="{t["dim"]}">@</tspan>'
           f'<tspan fill="{t["accent2"]}">{escape(cfg["host"])}</tspan></text>',
           f'<rect x="{x}" y="{y + 15}" width="190" height="2" fill="{t["border"]}" class="info" '
           f'style="animation-delay:{delay + 120}ms"/>']
    y += 46
    for i, (key, value) in enumerate(cfg["fields"]):
        d = delay + 240 + i * 120
        out.append(f'<text x="{x}" y="{y}" class="info kv" style="animation-delay:{d}ms">'
                   f'<tspan fill="{t["accent"]}" font-weight="700">{escape(key)}</tspan>'
                   f'<tspan x="{x + 96}" fill="{t["text"]}">{escape(value)}</tspan></text>')
        y += 27
    d = delay + 240 + len(cfg["fields"]) * 120
    for i, col in enumerate(t["blocks"]):
        out.append(f'<rect x="{x + i * 30}" y="{y - 10}" width="26" height="22" rx="3" fill="{col}" class="info" '
                   f'style="animation-delay:{d + i * 60}ms"/>')
    out.append(f'<rect x="{x + 248}" y="{y - 8}" width="9" height="18" fill="{t["accent"]}" class="cursor"/>')
    return "\n".join(out)


def header_svg(grid, rows, cols, cfg, t):
    px, py = 28, 64
    ix = px + cols * CW + 40
    width = int(ix + 512)
    height = int(py + rows * LH + 30)
    css, portrait = portrait_svg(grid, px, py)
    n = len(cfg["fields"])
    info_y = int(py + max(20, (rows * LH - (46 + n * 27 + 20)) / 2))   # centre the panel next to the portrait
    dots = "".join(f'<circle cx="{24 + i * 20}" cy="22" r="6" fill="{c}"/>' for i, c in enumerate(DOTS))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="t">
<title id="t">{escape(cfg["alt"])}</title>
<style>
text{{font-family:{FONT}}}
.row{{font-size:{FS}px;opacity:0;animation:in .5s ease-out forwards}}
{css}
.info{{opacity:0;animation:slide .45s ease-out forwards}}
.kv{{font-size:14px}}
.title{{font-size:20px;font-weight:700}}
.cursor{{animation:blink 1.1s steps(1) infinite}}
@keyframes in{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes slide{{from{{opacity:0;transform:translateX(12px)}}to{{opacity:1;transform:none}}}}
@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.row,.info,.cursor{{animation:none;opacity:1}}}}
</style>
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>
<path d="M1 13a12 12 0 0 1 12-12h{width - 26}a12 12 0 0 1 12 12v31H1z" fill="{t["bar"]}"/>
<line x1="1" y1="44" x2="{width - 1}" y2="44" stroke="{t["border"]}"/>
{dots}
<text x="{width / 2}" y="27" text-anchor="middle" font-size="13" fill="{t["dim"]}">{escape(cfg["user"])}@{escape(cfg["host"])}: ~ $ neofetch</text>
{portrait}
{info_svg(cfg, t, ix, info_y, rows * 28 + 200)}
</svg>
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--photo", type=Path, default=Path(__file__).parent / "photo.jpg")
    ap.add_argument("--config", type=Path, default=Path(__file__).parent / "profile.json")
    ap.add_argument("--out", type=Path, default=ROOT / "assets")
    ap.add_argument("--cols", type=int, default=96, help="characters per portrait line")
    ap.add_argument("--model", default="u2net_human_seg", help="rembg model used to remove the background")
    args = ap.parse_args()

    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    img, mask = crop_head_and_shoulders(*cut_out(args.photo, args.model))
    grids, rows = to_grid(img, mask, args.cols)
    args.out.mkdir(parents=True, exist_ok=True)
    for theme, t in THEMES.items():
        path = args.out / f"header_{theme}.svg"
        path.write_text(header_svg(grids[theme], rows, args.cols, cfg, t), encoding="utf-8")
        print(f"wrote {path} ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
