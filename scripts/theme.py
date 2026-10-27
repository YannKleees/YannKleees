from html import escape

SANS = 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
MONO = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace'

# Backgrounds stay transparent so the SVGs sit on GitHub's own light (#ffffff) and dark (#0d1117) pages.
THEMES = {
    "light": {
        "ink": "#1f2328",
        "secondary": "#59636e",
        "muted": "#818b98",
        "rule": "#d1d9e0",
        "accent": "#d9411e",
        "grays": ["#32383f", "#59636e", "#818b98"],
    },
    "dark": {
        "ink": "#e6edf3",
        "secondary": "#9198a1",
        "muted": "#6e7681",
        "rule": "#30363d",
        "accent": "#f25a2c",
        "grays": ["#b7bdc8", "#8b949e", "#6e7681"],
    },
}


def svg(width, height, title, body, style=""):
    return "\n".join(
        [
            (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
                f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">'
            ),
            f'<title id="title">{escape(title)}</title>',
            f"<style>{style}</style>" if style else "",
            body,
            "</svg>",
            "",
        ]
    )


def text(x, y, s, size, fill, font=SANS, weight=400, anchor="start", extra=""):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family=\'{font}\' font-size="{size}" font-weight="{weight}" '
        f'fill="{fill}" text-anchor="{anchor}"{extra}>{escape(s)}</text>'
    )


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
