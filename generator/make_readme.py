"""Write README.md from generator/projects.json: the projects grouped by what I learned from them.

    python generator/make_readme.py

Each project is a folder that opens to its tech stack, a screenshot if there is one, how it works,
a short text and the links. Edit projects.json, not README.md.
"""
import json
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = json.loads((HERE / "projects.json").read_text(encoding="utf-8"))
PROFILE = json.loads((HERE / "profile.json").read_text(encoding="utf-8"))


def picture(path, alt, width="100%"):
    """An image in two versions, so it fits GitHub's light and dark theme."""
    size = f' width="{width}"' if width else ""
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/{path}_dark.svg">'
            f'<img src="assets/{path}_light.svg"{size} alt="{escape(alt, quote=True)}"></picture>')


def button(href, name, alt):
    return f'<a href="{href}">{picture(f"buttons/{name}", alt, width="")}</a>'


def stack_names(project):
    names = []
    for entry in project["stack"]:
        slug, _, label = entry.partition(":")
        names.append(label or slug)
    return ", ".join(names)


def folder(p):
    lines = [
        "<details>",
        f'<summary><code>{escape(p["when"])}</code> &nbsp;<b>{escape(p["name"])}/</b> &nbsp;{escape(p["tagline"])}</summary>',
        "<br>",
        "",
        escape(p["context"]),
        "",
        picture(f'stack/{p["slug"]}', f'Tech stack of {p["name"]}: {stack_names(p)}'),
        "",
    ]
    shot = p.get("shot")
    if shot:
        lines += [f'<img src="{shot["url"]}" width="{shot["width"]}" alt="{escape(shot["alt"], quote=True)}">', ""]
    lines += [
        picture(f'flow/{p["slug"]}', f'How {p["name"]} works: ' + ", then ".join(
            step[0].lower() if isinstance(step[0], str) else " and ".join(s[0].lower() for s in step) for step in p["flow"])),
        "",
        p["text"],
        "",
    ]
    links = []
    if p.get("repo"):
        links.append(button(p["repo"], "repo", f'View the {p["name"]} repository'))
    if p.get("demo"):
        links.append(button(p["demo"], "demo", f'Open the {p["name"]} live demo'))
    if links:
        lines += ["\n".join(links), ""]
    lines += ["<br>", "</details>", ""]
    return "\n".join(lines)


def main():
    out = [
        picture("profile", PROFILE["alt"]),
        "",
        "<p>",
        button("https://www.linkedin.com/in/yann-klees-a0b8a6334", "linkedin", "LinkedIn"),
        button("mailto:yannklees@gmail.com", "email", "Email yannklees@gmail.com"),
        "</p>",
        "",
        "Open a folder for the tech stack, how it works and the code.",
        "",
    ]
    for area in DATA["areas"]:
        projects = [p for p in DATA["projects"] if p["area"] == area["id"]]
        projects.sort(key=lambda p: (p["spans"][-1][1], p["spans"][0][0]), reverse=True)  # newest first
        out += [f'### {area["title"]}', "", area["learned"], ""]
        out += [folder(p) for p in projects]
    (ROOT / "README.md").write_text("\n".join(out).rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"README.md written: {len(DATA['projects'])} projects in {len(DATA['areas'])} areas")


if __name__ == "__main__":
    main()
