"""Draw the pictures of the profile from generator/projects.json, in light and dark versions.

    python generator/make_visuals.py

Writes, per project, the "how it works" flow (assets/flow/) and the tech stack with icons
(assets/stack/), plus the link buttons (assets/buttons/). The icons in icons.json are from Simple Icons (CC0).
"""
import json
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

THEMES = {
    "light": dict(page="#ffffff", panel="#f6f8fa", border="#d8dee4", text="#1f2328", dim="#656d76", accent="#0969da", soft="#8c959f"),
    "dark": dict(page="#0d1117", panel="#161b22", border="#30363d", text="#e6edf3", dim="#8d96a0", accent="#4493f8", soft="#6e7681"),
}

DATA = json.loads((HERE / "projects.json").read_text(encoding="utf-8"))
PROJECTS = DATA["projects"]
ICONS = json.loads((HERE / "icons.json").read_text(encoding="utf-8"))

W, GAP, BOX_H, STACK_GAP = 880, 28, 72, 8


def text_width(label, size=13.0):
    wide, narrow = set("mwMW@%"), set("ijlrtf.,:;!|' -()")
    return sum(0.80 if c in wide else 0.33 if c in narrow else 0.56 for c in label) * size


# ------------------------------------------------------------------ flow: how a project works

def step(x, y, w, h, num, name, detail, t):
    mid = y + h / 2
    return (f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{w - 1}" height="{h - 1}" rx="10" fill="{t["panel"]}" stroke="{t["border"]}"/>'
            f'<text x="{x + 14}" y="{mid - 5}" font-size="11" font-weight="600" fill="{t["accent"]}">{num:02d}</text>'
            f'<text x="{x + 36}" y="{mid - 5}" font-size="14.5" font-weight="600" fill="{t["text"]}">{escape(name)}</text>'
            f'<text x="{x + 14}" y="{mid + 15}" font-size="12.5" fill="{t["dim"]}">{escape(detail)}</text>')


def flow(steps, t):
    """Each step is [name, what it does]; a list of steps runs side by side."""
    n = len(steps)
    is_group = lambda s: isinstance(s[0], list)
    stacked = any(is_group(s) for s in steps)
    height = 2 * BOX_H + STACK_GAP if stacked else BOX_H
    bw = (W - (n - 1) * GAP) / n
    parts, num = [], 1
    for i, s in enumerate(steps):
        x = i * (bw + GAP)
        group = s if is_group(s) else [s]
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


# ------------------------------------------------------------------ stack: the technologies, with their icons

def luminance(hex_colour):
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def stack_item(entry):
    """'python' uses the icon and its usual name, 'huggingface:GLiNER' renames it, anything else is plain text."""
    slug, _, label = entry.partition(":")
    if slug in ICONS:
        return ICONS[slug], label or ICONS[slug]["label"]
    return None, entry


def stack(entries, t, theme):
    chip_h, pad, gap, x, y, parts = 34, 12, 8, 0, 0, []
    for entry in entries:
        icon, label = stack_item(entry)
        w = pad * 2 + text_width(label, 13.5) + (24 if icon else 0)
        if x and x + w > W:
            x, y = 0, y + chip_h + gap
        parts.append(f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{w - 1:.1f}" height="{chip_h - 1}" rx="17" fill="{t["panel"]}" stroke="{t["border"]}"/>')
        tx = x + pad
        if icon:
            colour = icon["hex"]
            # a brand colour that would vanish on this background is drawn in the text colour instead
            if (theme == "dark" and luminance(colour) < 0.22) or (theme == "light" and luminance(colour) > 0.75):
                colour = t["text"]
            parts.append(f'<path transform="translate({tx:.1f},{y + 9}) scale(0.667)" fill="{colour}" d="{icon["path"]}"/>')
            tx += 24
        parts.append(f'<text x="{tx:.1f}" y="{y + 21.5}" font-size="13.5" font-weight="500" fill="{t["text"]}">{escape(label)}</text>')
        x += w + gap
    height = y + chip_h
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" '
            f'font-family="{SANS}">\n{"".join(parts)}\n</svg>\n')


# ------------------------------------------------------------------ buttons

BUTTON_ICONS = {
    "linkedin": '<path transform="translate({x},{y}) scale(0.58)" fill="{c}" d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.850 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.140 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>',
    "mail": '<g transform="translate({x},{y})" fill="none" stroke="{c}" stroke-width="1.5"><rect x="0.75" y="1.75" width="12.5" height="10.5" rx="2"/><path d="M1.5 3.5l5.5 4.2 5.5-4.2"/></g>',
    "demo": '<g transform="translate({x},{y})" fill="none" stroke="{c}" stroke-width="1.5" stroke-linejoin="round"><circle cx="7" cy="7" r="6.25"/><path d="M5.5 4.6v4.8l4-2.4z"/></g>',
    "repo": '<g transform="translate({x},{y})" fill="none" stroke="{c}" stroke-width="1.5" stroke-linejoin="round"><path d="M1 2.5h4l1.4 1.7H13v7.8H1z"/></g>',
}


def button(label, icon, t):
    wide, narrow = set("mwMW@%"), set("ijlrtf.,:;!|' -")
    w = int(sum(10.5 if c in wide else 4.2 if c in narrow else 7.0 for c in label) + 66)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="32" viewBox="0 0 {w} 32" font-family="{SANS}">
<rect x="0.5" y="0.5" width="{w - 1}" height="31" rx="8" fill="{t["panel"]}" stroke="{t["border"]}"/>
{BUTTON_ICONS[icon].format(x=13, y=9, c=t["text"])}
<text x="35" y="20.5" font-size="13" font-weight="500" fill="{t["text"]}">{escape(label)}</text>
<text x="{w - 16}" y="20.5" font-size="12" text-anchor="middle" fill="{t["dim"]}">↗</text>
</svg>
'''


BUTTONS = {"linkedin": ("LinkedIn", "linkedin"), "email": ("yannklees@gmail.com", "mail"),
           "repo": ("View repository", "repo"), "demo": ("Live demo", "demo")}


def main():
    assets = ROOT / "assets"
    for folder in ("flow", "stack", "buttons"):
        (assets / folder).mkdir(parents=True, exist_ok=True)
    wanted = {f"{p['slug']}_{theme}.svg" for p in PROJECTS for theme in THEMES}
    for folder in ("flow", "stack"):
        for old in (assets / folder).glob("*.svg"):
            if old.name not in wanted:
                old.unlink()
    for theme, t in THEMES.items():
        for p in PROJECTS:
            (assets / "flow" / f"{p['slug']}_{theme}.svg").write_text(flow(p["flow"], t), encoding="utf-8")
            (assets / "stack" / f"{p['slug']}_{theme}.svg").write_text(stack(p["stack"], t, theme), encoding="utf-8")
        for name, (label, icon) in BUTTONS.items():
            (assets / "buttons" / f"{name}_{theme}.svg").write_text(button(label, icon, t), encoding="utf-8")
    print(f"{len(PROJECTS)} projects: flows, stacks and buttons written to assets/")


if __name__ == "__main__":
    main()
