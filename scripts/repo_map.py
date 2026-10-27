import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

import numpy as np
import requests
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfTransformer

from theme import MONO, THEMES, svg, text, write

USER = "YannKleees"
ROOT = Path(__file__).resolve().parent.parent
SHOWCASE = {"hyperreimpute"}
# Public repos kept off the map until they are cleaned up.
EXCLUDE = {"Orthodontic", "hci_rpoject"}

# Most specific first: a repo's primary topic is the first one it matches.
TOPICS = {
    "computer-vision": "cv2 torchvision ultralytics easyocr",
    "nlp": "transformers gliner spacy nltk sentence_transformers",
    "recommender-systems": "implicit lightfm faiss",
    "bioinformatics": "cobra siibra bio",
    "desktop-app": "pywebview pyaudiowpatch",
    "web-app": "flask fastapi react express next streamlit gradio",
    "deep-learning": "torch tensorflow keras",
    "machine-learning": "sklearn catboost xgboost lightgbm hyperimpute optuna",
    "statistics": "scipy statsmodels",
    "data-visualization": "matplotlib seaborn plotly altair",
}
ALIASES = {
    "scikit_learn": "sklearn",
    "opencv_python": "cv2",
    "opencv_python_headless": "cv2",
    "pillow": "pil",
    "pyyaml": "yaml",
    "beautifulsoup4": "bs4",
    "python_dotenv": "dotenv",
    "biopython": "bio",
    "pytorch": "torch",
    "webview": "pywebview",
    "winrt_runtime": "winrt",
    "winrt_windows": "winrt",
}
NOISE = {
    "pip",
    "setuptools",
    "wheel",
    "ipython",
    "ipykernel",
    "jupyter",
    "notebook",
    "tqdm",
    "packaging",
    "python",
    "r",
    "__future__",
}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "env", "__pycache__", "site-packages", "dist", "build", ".next"}

LANG_ICONS = {
    "python": "py",
    "jupyter notebook": "py",
    "r": "r",
    "java": "java",
    "typescript": "ts",
    "javascript": "js",
    "rust": "rust",
    "html": "html",
}
ML_ICONS = {"sklearn": "sklearn", "torch": "pytorch", "tensorflow": "tensorflow", "cv2": "opencv"}
TOOL_ICONS = {"flask": "flask", "fastapi": "fastapi", "react": "react", "express": "express"}
ICON_NAMES = {
    "py": "Python",
    "r": "R",
    "java": "Java",
    "ts": "TypeScript",
    "js": "JavaScript",
    "rust": "Rust",
    "html": "HTML",
    "sklearn": "scikit-learn",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "opencv": "OpenCV",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "react": "React",
    "express": "Express",
}
DATA_LIBS = {
    "pandas": "pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "statsmodels": "statsmodels",
    "matplotlib": "Matplotlib",
    "seaborn": "seaborn",
    "plotly": "Plotly",
    "catboost": "CatBoost",
    "xgboost": "XGBoost",
    "networkx": "NetworkX",
}

http = requests.Session()
if token := os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"):
    http.headers["Authorization"] = f"Bearer {token}"


def api(path, **params):
    r = http.get(f"https://api.github.com{path}", params=params, timeout=30)
    r.raise_for_status()
    return r


def canonical(name):
    name = name.strip().lower().replace("-", "_").split(".")[0]
    return ALIASES.get(name, name)


def requirement(line):
    m = re.match(r"\s*([A-Za-z0-9_.\-]+)", line)
    return m.group(1) if m and not line.lstrip().startswith(("#", "-")) else None


def declared(path):
    name = path.name.lower()
    s = path.read_text(encoding="utf-8", errors="ignore")
    if name.startswith("requirements") and name.endswith(".txt"):
        return [requirement(x) for x in s.splitlines()]
    if name == "pyproject.toml":
        project = tomllib.loads(s).get("project", {})
        deps = project.get("dependencies", []) + [
            x for v in project.get("optional-dependencies", {}).values() for x in v
        ]
        return [requirement(x) for x in deps]
    if name in ("environment.yml", "environment.yaml"):
        return re.findall(r"^\s*-\s*([A-Za-z0-9_.\-]+)", s, re.MULTILINE)
    if name == "package.json":
        return list(json.loads(s).get("dependencies", {}))
    if name == "description":
        fields = re.findall(r"^(?:Imports|Depends):(.*(?:\n\s+.*)*)", s, re.MULTILINE)
        return [re.sub(r"\(.*\)", "", x) for f in fields for x in f.split(",")]
    return []


def imported(path):
    s = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix == ".ipynb":
        cells = json.loads(s).get("cells", [])
        s = "\n".join("".join(c["source"]) for c in cells if c.get("cell_type") == "code")
    if path.suffix == ".R":
        return re.findall(r"(?:library|require)\(\s*['\"]?([\w.]+)", s)
    return [a or b for a, b in re.findall(r"^\s*(?:from\s+(\w+)|import\s+(\w+))", s, re.MULTILINE)]


def libraries(repo_dir):
    found, local = set(), set()
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        local.update(canonical(d) for d in dirs)
        for f in files:
            p = Path(root) / f
            if p.suffix == ".py":
                local.add(canonical(p.stem))
            if p.suffix in (".py", ".ipynb", ".R") and p.stat().st_size < 20_000_000:
                found.update(imported(p))
            found.update(x for x in declared(p) if x)
    stdlib = {canonical(x) for x in sys.stdlib_module_names}
    return sorted({canonical(x) for x in found} - stdlib - local - NOISE - {""})


def commits(name):
    r = api(f"/repos/{USER}/{name}/commits", author=USER, per_page=1)
    m = re.search(r'page=(\d+)>; rel="last"', r.headers.get("Link", ""))
    return int(m.group(1)) if m else len(r.json())


def collect():
    repos = api(f"/users/{USER}/repos", type="owner", per_page=100).json()
    repos = [r for r in repos if not r["fork"] and not r["archived"] and r["name"] not in EXCLUDE]
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        for r in sorted(repos, key=lambda r: r["name"].lower()):
            langs = list(api(f"/repos/{USER}/{r['name']}/languages").json())
            if not langs:
                continue
            path = Path(tmp) / r["name"]
            subprocess.run(["git", "clone", "-q", "--depth", "1", r["clone_url"], str(path)], check=True)
            libs = libraries(path)
            topics = [t for t, words in TOPICS.items() if set(words.split()) & set(libs)] + r["topics"]
            out.append(
                {
                    "name": r["name"],
                    "url": r["html_url"],
                    "description": r["description"] or "",
                    "languages": [x.lower() for x in langs],
                    "libraries": libs,
                    "topics": list(dict.fromkeys(topics)),
                    "topic": topics[0] if topics else "software",
                    "commits": commits(r["name"]),
                    "showcase": r["name"] in SHOWCASE,
                }
            )
    return out


def embed(repos):
    features = [set(r["libraries"]) | set(r["topics"]) | {f"lang:{x}" for x in r["languages"]} for r in repos]
    vocab = sorted(set().union(*features))
    x = np.array([[v in f for v in vocab] for f in features], dtype=float)
    x = TfidfTransformer().fit_transform(x).toarray()
    k = min(2, len(repos) - 1, len(vocab))
    xy = PCA(n_components=k, random_state=0).fit_transform(x) if k > 0 else np.zeros((len(repos), 0))
    xy = np.pad(xy, ((0, 0), (0, 2 - xy.shape[1])))
    for r, (a, b) in zip(repos, xy):
        r["x"], r["y"] = round(float(a), 4), round(float(b), 4)
    return repos


W, H = 880, 420
LEFT, RIGHT, TOP, BOTTOM = 56, 56, 48, 84
CHAR = 7.4


def scale(values, lo, hi):
    a, b = min(values), max(values)
    return (lambda v: (lo + hi) / 2) if a == b else (lambda v: lo + (v - a) / (b - a) * (hi - lo))


def label_box(x, y, r, name, topic, side):
    w, h = max(len(name), len(topic)) * CHAR, 30
    gap = r + 8
    return {
        "right": (x + gap, y - 12, w, h, "start"),
        "left": (x - gap - w, y - 12, w, h, "end"),
        "above": (x - w / 2, y - gap - h, w, h, "middle"),
        "below": (x - w / 2, y + gap, w, h, "middle"),
    }[side]


def overlaps(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def layout(repos):
    sx = scale([r["x"] for r in repos], LEFT + 24, W - RIGHT - 24)
    sy = scale([-r["y"] for r in repos], TOP + 24, H - BOTTOM - 24)
    most = max(r["commits"] for r in repos) or 1
    dots = [(sx(r["x"]), sy(-r["y"]), 5 + 9 * (r["commits"] / most) ** 0.5) for r in repos]
    ox, oy = sx(0), sy(0)
    # The axis labels sit just past the ends of the axis lines; dot labels must avoid them too.
    boxes = [(x - r, y - r, 2 * r, 2 * r) for x, y, r in dots] + [
        (W - RIGHT + 4, oy - 10, 30, 16),
        (ox - 16, TOP - 24, 32, 16),
    ]
    placed = []
    for i in sorted(range(len(repos)), key=lambda i: -dots[i][2]):
        x, y, r = dots[i]
        for side in ("right", "left", "above", "below"):
            bx, by, bw, bh, anchor = label_box(x, y, r, repos[i]["name"], repos[i]["topic"], side)
            box = (bx, by, bw, bh)
            inside = bx >= 0 and bx + bw <= W and by >= 0 and by + bh <= H - BOTTOM + 30
            clear = not any(overlaps(box, b) for j, b in enumerate(boxes) if j != i)
            if inside and clear and not any(overlaps(box, b) for b, _ in placed):
                break
        placed.append((box, (i, anchor)))
    labels = {i: (box, anchor) for box, (i, anchor) in placed}
    return dots, labels, (ox, oy)


STYLE = """
.d { animation: settle .8s cubic-bezier(.2, .7, .2, 1) both; transform-box: fill-box; transform-origin: center; }
@keyframes settle { from { opacity: 0; transform: translateY(10px) scale(.6); } to { opacity: 1; transform: none; } }
@media (prefers-reduced-motion: reduce) { .d { animation: none; } }
"""


def draw(repos, theme):
    t = THEMES[theme]
    dots, labels, (ox, oy) = layout(repos)
    topics = sorted({r["topic"] for r in repos})
    shade = {k: t["grays"][i % len(t["grays"])] for i, k in enumerate(topics)}
    body = [
        f'<line x1="{LEFT}" y1="{oy:.1f}" x2="{W - RIGHT}" y2="{oy:.1f}" stroke="{t["rule"]}" stroke-width="1"/>',
        f'<line x1="{ox:.1f}" y1="{TOP}" x2="{ox:.1f}" y2="{H - BOTTOM}" stroke="{t["rule"]}" stroke-width="1"/>',
        text(W - RIGHT + 8, oy + 4, "PC1", 11, t["muted"], MONO),
        text(ox, TOP - 12, "PC2", 11, t["muted"], MONO, anchor="middle"),
    ]
    order = sorted(range(len(repos)), key=lambda i: (repos[i]["x"], repos[i]["y"]))
    for k, i in enumerate(order):
        r, (x, y, rad) = repos[i], dots[i]
        fill = t["accent"] if r["showcase"] else shade[r["topic"]]
        (bx, by, bw, _), anchor = labels[i]
        lx = {"start": bx, "end": bx + bw, "middle": bx + bw / 2}[anchor]
        body += [
            f'<g class="d" style="animation-delay:{min(k * 0.12, 1.1):.2f}s">',
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" fill="{fill}"/>',
            text(lx, by + 11, r["name"], 12, t["ink"], MONO, 500 if r["showcase"] else 400, anchor),
            text(lx, by + 26, r["topic"], 11, t["muted"], MONO, anchor=anchor),
            "</g>",
        ]
    body += [
        f'<line x1="{LEFT}" y1="{H - 44}" x2="{W - RIGHT}" y2="{H - 44}" stroke="{t["rule"]}" stroke-width="1"/>',
        text(LEFT, H - 20, "Projects embedded by tools and topics, PCA", 12, t["secondary"], MONO),
        text(W - RIGHT, H - 20, "size = my commits", 12, t["muted"], MONO, anchor="end"),
    ]
    title = "Map of public projects, embedded by tools and topics with PCA: " + ", ".join(
        f"{r['name']} ({r['topic']})" for r in repos
    )
    return svg(W, H, title, "\n".join(body), STYLE)


def toolbox(repos):
    langs = {x for r in repos for x in r["languages"]}
    libs = {x for r in repos for x in r["libraries"]}
    icons = list(dict.fromkeys(v for k, v in LANG_ICONS.items() if k in langs))
    icons += [v for k, v in ML_ICONS.items() if k in libs] + [v for k, v in TOOL_ICONS.items() if k in libs]
    data = [v for k, v in DATA_LIBS.items() if k in libs]
    lines = [
        f'<img src="https://skillicons.dev/icons?i={",".join(icons)}&perline=12" height="40" alt="{", ".join(ICON_NAMES[x] for x in icons)}">'
    ]
    if data:
        lines += ["", "Data and visualisation: " + ", ".join(data) + "."]
    return "\n".join(lines)


def replace_section(readme, name, content):
    s = readme.read_text(encoding="utf-8")
    pattern = re.compile(rf"(<!-- {name}:start -->).*?(<!-- {name}:end -->)", re.DOTALL)
    s = pattern.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(2)}", s)
    readme.write_text(s, encoding="utf-8", newline="\n")


def main():
    repos = embed(collect())
    for theme in THEMES:
        write(ROOT / "assets" / f"repo_map_{theme}.svg", draw(repos, theme))
    write(ROOT / "assets" / "repo_map.json", json.dumps(repos, indent=2) + "\n")
    replace_section(ROOT / "README.md", "toolbox", toolbox(repos))
    for r in repos:
        print(f"{r['name']:24} {r['topic']:20} commits={r['commits']:<4} {' '.join(r['libraries'])}")


if __name__ == "__main__":
    main()
