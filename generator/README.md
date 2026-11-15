# Profile image generators

| Script | Draws |
|---|---|
| `make_header.py` | the profile card with the ASCII portrait (`assets/profile_*.svg`), from `photo.jpg` and `profile.json` |
| `make_visuals.py` | per project the flow (`assets/flow/`) and the tech stack with icons (`assets/stack/`) and the buttons (`assets/buttons/`) |
| `make_readme.py` | `README.md` itself: the projects grouped by what I learned (`areas` in `projects.json`), each as a folder that opens |
| `make_stats.py` | contributions in the last year and the languages of my public repositories (`assets/stats_*.svg`) |

```
pip install -r generator/requirements.txt
python generator/make_header.py --photo path/to/photo.jpg
python generator/make_visuals.py
python generator/make_stats.py        # uses GITHUB_TOKEN or a logged-in gh CLI
python generator/make_readme.py
```

The portrait: [rembg](https://github.com/danielgatis/rembg) cuts the person out of the photo, the image is cropped to head and shoulders and sharpened, and each cell becomes a character from ` .:-=+*#%@` coloured like the photo. Options: `--cols` (portrait width in characters), `--model` (rembg model) and `--mask` (your own black-and-white mask instead of rembg). Edit the text next to the portrait in `profile.json`.

Every project is one entry in `projects.json`: its name, dates, context, tech stack, flow, text and links. Add or change an entry there and run `make_visuals.py` and `make_readme.py`; do not edit `README.md` by hand. In `stack`, a name from `icons.json` (for example `python`) gets its icon, `huggingface:GLiNER` shows that icon with another label, and anything else is shown as plain text. The icons are from [Simple Icons](https://simpleicons.org) (CC0).
