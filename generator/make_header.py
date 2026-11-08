"""Turn a photo into the profile header: an ASCII portrait next to a short profile.

    python generator/make_header.py --photo generator/photo.jpg

Steps: remove the background with rembg, crop to head and shoulders, map each cell of the photo to a
character coloured like the photo, and write assets/profile_light.svg and assets/profile_dark.svg.
The text on the right comes from profile.json.
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
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

THEMES = {
    "light": dict(bg="#ffffff", border="#d8dee4", text="#1f2328", dim="#656d76"),
    "dark": dict(bg="#0d1117", border="#30363d", text="#e6edf3", dim="#8d96a0"),
}


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
    blur = cv2.GaussianBlur(gray, (0, 0), 6)
    gray = cv2.addWeighted(gray, 1.8, blur, -0.8, 0)           # sharpen eyes, brows and mouth
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
                # dark background: bright parts get dense characters; light background: dark parts do
                v, lo = (g[r, c], 3) if theme == "dark" else (1 - g[r, c], 2)
                ch = RAMP[min(len(RAMP) - 1, lo + int(v * (len(RAMP) - lo)))]
                b, gr, rd = (int(v) for v in small[r, c])
                if theme == "dark":                          # lift dark colours off the dark background
                    rd, gr, b = (int(v + (255 - v) * 0.12) for v in (rd, gr, b))
                else:                                        # darker and more saturated on white
                    h, s, v = cv2.cvtColor(np.uint8([[[b, gr, rd]]]), cv2.COLOR_BGR2HSV)[0, 0].astype(int)
                    b, gr, rd = (int(x) for x in cv2.cvtColor(
                        np.uint8([[[h, min(255, int(s * 1.6)), int(v * 0.6)]]]), cv2.COLOR_HSV2BGR)[0, 0])
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
                         f'style="animation-delay:{r * 18}ms">{"".join(spans)}</text>')
    return css, "\n".join(lines)


def info_svg(cfg, t, x, y):
    out = [f'<text x="{x}" y="{y}" font-size="28" font-weight="600" fill="{t["text"]}">{escape(cfg["name"])}</text>',
           f'<text x="{x}" y="{y + 28}" font-size="15" fill="{t["dim"]}">{escape(cfg["tagline"])}</text>']
    y += 74
    for label, value in cfg["fields"]:
        values = value if isinstance(value, list) else [value]
        out.append(f'<text x="{x}" y="{y}" font-size="11" font-weight="600" letter-spacing="1" fill="{t["dim"]}">'
                   f'{escape(label.upper())}</text>')
        for i, v in enumerate(values):
            out.append(f'<text x="{x + 104}" y="{y + i * 21}" font-size="14" fill="{t["text"]}">{escape(v)}</text>')
        y += 21 * len(values) + 14
    return "\n".join(out), y


def header_svg(grid, rows, cols, cfg, t):
    px, py = 24, 24
    ix = int(px + cols * CW + 44)
    width = ix + 440
    height = int(py + rows * LH + 24)
    css, portrait = portrait_svg(grid, px, py)
    _, end = info_svg(cfg, t, ix, 0)
    info, _ = info_svg(cfg, t, ix, int((height - (end - 14)) / 2) + 22)    # centred next to the portrait
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="t">
<title id="t">{escape(cfg["alt"])}</title>
<style>
.row{{font-family:{FONT};font-size:{FS}px;opacity:0;animation:in .6s ease-out forwards}}
{css}
@keyframes in{{to{{opacity:1}}}}
@media (prefers-reduced-motion:reduce){{.row{{animation:none;opacity:1}}}}
</style>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>
{portrait}
<g font-family="{SANS}">
{info}
</g>
</svg>
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--photo", type=Path, default=Path(__file__).parent / "photo.jpg")
    ap.add_argument("--config", type=Path, default=Path(__file__).parent / "profile.json")
    ap.add_argument("--out", type=Path, default=ROOT / "assets")
    ap.add_argument("--cols", type=int, default=96, help="characters per portrait line")
    ap.add_argument("--model", default="u2net_human_seg", help="rembg model used to remove the background")
    ap.add_argument("--mask", type=Path, help="use this black-and-white mask instead of rembg")
    args = ap.parse_args()

    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    if args.mask:
        img = cv2.cvtColor(np.array(Image.open(args.photo).convert("RGB")), cv2.COLOR_RGB2BGR)
        mask = np.array(Image.open(args.mask).convert("L").resize(img.shape[1::-1])) > 127
    else:
        img, mask = cut_out(args.photo, args.model)
    img, mask = crop_head_and_shoulders(img, mask)
    grids, rows = to_grid(img, mask, args.cols)
    args.out.mkdir(parents=True, exist_ok=True)
    for theme, t in THEMES.items():
        path = args.out / f"profile_{theme}.svg"
        path.write_text(header_svg(grids[theme], rows, args.cols, cfg, t), encoding="utf-8")
        print(f"wrote {path} ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
