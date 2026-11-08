# Profile image generators

| Script | Draws |
|---|---|
| `make_header.py` | the profile card with the ASCII portrait (`assets/profile_*.svg`), from `photo.jpg` and `profile.json` |
| `make_visuals.py` | the flow of each project (`assets/flow/`) and the buttons (`assets/buttons/`) |
| `make_stats.py` | contributions in the last year and the languages of my public repositories (`assets/stats_*.svg`) |

```
pip install -r generator/requirements.txt
python generator/make_header.py --photo path/to/photo.jpg
python generator/make_visuals.py
python generator/make_stats.py        # uses GITHUB_TOKEN or a logged-in gh CLI
```

The portrait: [rembg](https://github.com/danielgatis/rembg) cuts the person out of the photo, the image is cropped to head and shoulders and sharpened, and each cell becomes a character from ` .:-=+*#%@` coloured like the photo. Options: `--cols` (portrait width in characters), `--model` (rembg model) and `--mask` (your own black-and-white mask instead of rembg). Edit the text next to the portrait in `profile.json` and the project flows in `make_visuals.py`.
