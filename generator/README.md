# Header generator

Turns a photo into the ASCII header at the top of the profile.

**On GitHub:** upload a new photo as `generator/photo.jpg` (Add file → Upload files). The *Rebuild header* workflow removes the background, draws the portrait and commits the new `assets/header_light.svg` and `assets/header_dark.svg`. Change the text on the right in `profile.json`.

**Locally:**

```
pip install -r generator/requirements.txt
python generator/make_header.py --photo path/to/photo.jpg
```

How it works: [rembg](https://github.com/danielgatis/rembg) cuts the person out of the photo, the image is cropped to head and shoulders, and each cell becomes a character from ` .:-=+*#%@` (brighter means denser) coloured like the photo. The light and dark versions use different colour adjustments so the portrait reads on both backgrounds. Options: `--cols` (portrait width in characters, default 96) and `--model` (rembg model, default `u2net_human_seg`).
