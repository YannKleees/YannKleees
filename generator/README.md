# Profile image generators

Everything visual on the profile is drawn by these scripts.

| Script | Draws |
|---|---|
| `make_header.py` | the ASCII portrait header (`assets/header_*.svg`) and its window bar, from `photo.jpg` and `profile.json` |
| `make_visuals.py` | the "how it works" diagram of each project (`assets/diagrams/`) and the link buttons (`assets/links/`) |
| `make_stats.py` | contributions in the last year and the languages of my public repositories (`assets/stats_*.svg`) |

**On GitHub:** upload a new photo as `generator/photo.jpg` (Add file → Upload files) and the *Redraw profile images* workflow rebuilds everything. The stats are also redrawn every Monday. Change the text next to the portrait in `profile.json`.

**Locally:**

```
pip install -r generator/requirements.txt
python generator/make_header.py --photo path/to/photo.jpg
python generator/make_visuals.py
python generator/make_stats.py        # uses GITHUB_TOKEN or a logged-in gh CLI
```

The header: [rembg](https://github.com/danielgatis/rembg) cuts the person out of the photo, the image is cropped to head and shoulders and sharpened, and each cell becomes a character from ` .:-=+*#%@` coloured like the photo. On the dark version bright parts get dense characters, on the light version dark parts do, so the face reads on both backgrounds. Options: `--cols` (portrait width in characters, default 96), `--model` (rembg model) and `--mask` (use your own black-and-white mask instead of rembg).
