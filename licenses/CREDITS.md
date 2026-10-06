# Credits

## Fonts (embedded in every SVG as base64 WOFF2, Latin subset)

| Font | Use | Source | License |
| --- | --- | --- | --- |
| Outfit (variable) | Display text | The Outfit Project Authors — github.com/Outfitio/Outfit-Fonts | SIL Open Font License 1.1 — `OFL-Outfit.txt` |
| JetBrains Mono (variable) | Mono labels | The JetBrains Mono Project Authors — github.com/JetBrains/JetBrainsMono | SIL Open Font License 1.1 — `OFL-JetBrainsMono.txt` |

The WOFF2 files are the same self-hosted copies used by my Portfolio_01 site.

## Icons

Brand marks come from [Simple Icons](https://simpleicons.org) (icon data CC0 1.0), `simple-icons@16.34.0`:
Python, PyTorch, TensorFlow, OpenCV, scikit-learn, FastAPI, Docker, PostgreSQL, SQLite, Git, Linux, NumPy, pandas, Jupyter, Ultralytics (shown as YOLOv8), GitHub, Gmail.

LinkedIn is no longer shipped by current Simple Icons releases; its mark is taken from `simple-icons@9.21.0` (the last line that included it) and is used only to label the link to my LinkedIn profile.

All brand names and logos are trademarks of their respective owners and are used only to identify the technologies and platforms named.

The globe, pin, briefcase, cap, drone, chip and arrow graphics are drawn by hand in the SVGs.

## Portrait

My own photo (from Portfolio_01, `assets/img/hero-default.webp`), cropped and saved with its transparent background as `src/id.png`.

## Rebuilding

`python3 src/build.py` regenerates all five SVGs in `assets/` from `src/`.
