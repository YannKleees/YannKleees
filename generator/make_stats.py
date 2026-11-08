"""Draw my GitHub activity (contributions in the last year) and languages of my public repositories.

    python generator/make_stats.py            # needs a token: GITHUB_TOKEN, or a logged-in gh CLI

Writes assets/stats_light.svg and assets/stats_dark.svg.
"""
import json
import os
import subprocess
import urllib.request
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGIN = "YannKleees"
SKIP_LANGS = {"Jupyter Notebook"}       # notebook files are mostly outputs and images, not code
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

THEMES = {
    "light": dict(bg="#ffffff", border="#d8dee4", text="#1f2328", dim="#59636e", empty="#eff2f5",
                  scale=["#c6e0ff", "#80b8ff", "#3d8bfd", "#0969da"]),
    "dark": dict(bg="#0d1117", border="#30363d", text="#e6edf3", dim="#8d96a0", empty="#161b22",
                 scale=["#0c2d6b", "#1158c7", "#388bfd", "#79c0ff"]),
}

QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions restrictedContributionsCount
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      nodes { name languages(first: 12, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } } }
    }
  }
}"""


def token():
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"]
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def fetch():
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
                                 headers={"Authorization": f"bearer {token()}", "User-Agent": "profile-stats"})
    return json.load(urllib.request.urlopen(req, timeout=60))["data"]["user"]


def languages(user, top=6):
    size, repos, colour = {}, {}, {}
    for repo in user["repositories"]["nodes"]:
        if repo["name"] == LOGIN:               # skip the profile repo itself
            continue
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            if name in SKIP_LANGS:
                continue
            size[name] = size.get(name, 0) + e["size"]
            repos[name] = repos.get(name, 0) + 1
            colour[name] = e["node"]["color"] or "#8d96a0"
    total = sum(size.values())
    ranked = sorted(size, key=size.get, reverse=True)
    rows = [(n, size[n] / total, repos[n], colour[n]) for n in ranked[:top]]
    rest = sum(size[n] for n in ranked[top:]) / total
    if rest >= 0.005:
        rows.append(("Other", rest, None, "#8d96a0"))
    return rows


def svg(user, t):
    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    counts = sorted(d["contributionCount"] for d in days if d["contributionCount"])
    q = [counts[int(len(counts) * f)] for f in (0.25, 0.5, 0.75)] if counts else [1, 2, 3]

    def level(c):
        return 0 if c == 0 else 1 + sum(c > x for x in q)

    W, cell, gap, x0, y0 = 880, 12, 3, 24, 74
    out = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{{H}}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>',
           f'<text x="24" y="36" font-size="13" fill="{t["dim"]}">'
           f'<tspan fill="{t["text"]}" font-weight="600">{cal["totalContributions"]}</tspan> contributions in the last year</text>']
    month_seen = None
    for wi, w in enumerate(weeks):
        x = x0 + wi * (cell + gap)
        first = date.fromisoformat(w["contributionDays"][0]["date"])
        if first.month != month_seen and first.day <= 7 and wi < len(weeks) - 2:
            out.append(f'<text x="{x}" y="{y0 - 8}" font-size="10.5" fill="{t["dim"]}">{first:%b}</text>')
            month_seen = first.month
        for d in w["contributionDays"]:
            dy = date.fromisoformat(d["date"]).isoweekday() % 7
            lv = level(d["contributionCount"])
            fill = t["empty"] if lv == 0 else t["scale"][lv - 1]
            out.append(f'<rect x="{x}" y="{y0 + dy * (cell + gap)}" width="{cell}" height="{cell}" rx="2.5" fill="{fill}" '
                       f'class="cell" style="animation-delay:{wi * 18}ms"><title>{d["date"]}: {d["contributionCount"]}</title></rect>')

    # languages
    ly = y0 + 7 * (cell + gap) + 40
    out.append(f'<text x="24" y="{ly}" font-size="11" font-weight="600" letter-spacing="1" fill="{t["dim"]}">LANGUAGES</text>'
               f'<text x="{W - 24}" y="{ly}" text-anchor="end" font-size="13" fill="{t["dim"]}">public repositories, by code size</text>')
    bx, by, bw = 24, ly + 14, W - 48
    x = bx
    rows = languages(user)
    out.append(f'<clipPath id="bar"><rect x="{bx}" y="{by}" width="{bw}" height="8" rx="4"/></clipPath><g clip-path="url(#bar)">')
    for name, share, _, colour in rows:
        out.append(f'<rect x="{x:.1f}" y="{by}" width="{share * bw + 0.5:.1f}" height="8" fill="{colour}"/>')
        x += share * bw
    out.append("</g>")
    lx, lyy = bx, by + 32
    for name, share, n, colour in rows:
        label = f"{name} {share * 100:.0f}%"
        w = len(label) * 7.2 + 40
        if lx + w > W - 24:
            lx, lyy = bx, lyy + 24
        out.append(f'<circle cx="{lx + 6}" cy="{lyy - 4}" r="5" fill="{colour}"/>'
                   f'<text x="{lx + 17}" y="{lyy}" font-size="12.5" fill="{t["text"]}">{escape(name)} '
                   f'<tspan fill="{t["dim"]}">{share * 100:.0f}%</tspan></text>')
        lx += w
    H = int(lyy + 22)
    body = "".join(out).replace("{H}", str(H - 1))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">
<title>{cal["totalContributions"]} GitHub contributions in the last year, and the languages of my public repositories</title>
<style>
.cell{{opacity:0;animation:pop .4s ease-out forwards}}
@keyframes pop{{from{{opacity:0}}to{{opacity:1}}}}
@media (prefers-reduced-motion:reduce){{.cell{{animation:none;opacity:1}}}}
</style>
{body}
</svg>
'''


def main():
    user = fetch()
    for theme, t in THEMES.items():
        path = ROOT / "assets" / f"stats_{theme}.svg"
        path.write_text(svg(user, t), encoding="utf-8")
        print("wrote", path)


if __name__ == "__main__":
    main()
