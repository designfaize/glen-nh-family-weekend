# Glen, NH Family Weekend

Family weekend guide for Glen, New Hampshire (basecamp: Yogi Bear's Jellystone Park — Glen Ellis), July 17–20, 2026. Hosted with GitHub Pages.

- **`index.html`** — the guide: day-by-day plan, live Jellystone activity calendar (campersapp embed), attractions, restaurants, and an interactive **itinerary builder** (drag & drop, saves to localStorage, shareable via `?p=` URL param).
- **`map.html`** — the illustrated Family Fun Map with a printable PDF download.
- **`assets/`** — map image, map PDF, Funspot logo.

## Editing

`index.html` is generated: edit `planner_snippet.html` (the itinerary builder) or the base guide, then rebuild with `python build_index.py` (expects the base guide at `../glen-nh-weekend-guide_7.html`). Test the planner logic with `node test_planner.js`.

⚠️ In `planner_snippet.html`, the `ITEMS` array order is load-bearing — share links store array indices. Append new items only; never reorder or delete.
