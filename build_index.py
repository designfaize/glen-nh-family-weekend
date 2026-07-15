import pathlib

dl = pathlib.Path(r"C:\Users\JohnJ\Downloads")
repo = pathlib.Path(r"C:\Users\JohnJ\Downloads\glen-nh-family-weekend")

html = (dl / "glen-nh-weekend-guide_7.html").read_text(encoding="utf-8")

# 1. Funspot logo replaces the dashed placeholder
old_div = '<div class="dh-logo">Funspot logo<br>goes here</div>'
new_img = '<img class="dh-logo" src="assets/funspot-logo.png" alt="Funspot — Largest Arcade in the World">'
assert old_div in html, "logo placeholder div not found"
html = html.replace(old_div, new_img)

old_css = (
    ".dh-logo{flex:0 0 156px;min-height:74px;border:2px dashed #c3b0e6;"
    "border-radius:10px;display:flex;align-items:center;justify-content:center;"
    "text-align:center;color:#8a7bb5;font-size:11px;font-weight:600;padding:8px;}"
)
new_css = ".dh-logo{flex:0 0 156px;width:156px;height:auto;align-self:center;display:block;}"
assert old_css in html, "logo placeholder css not found"
html = html.replace(old_css, new_css)

# 2. Hero pills: planner anchor + map page
old_pill = '<div class="basecamp">🏕️ Basecamp: <b>Yogi Bear\'s Jellystone Park — Glen Ellis</b>, 83 Glen Ellis Campground Rd, Glen, NH</div>'
assert old_pill in html, "basecamp pill not found"
html = html.replace(
    old_pill,
    old_pill
    + '\n    <div style="margin-top:2px;">'
    + '<a class="basecamp" href="#builder" style="color:#fff;text-decoration:none;">🧩 Build your itinerary</a>'
    + '\n    <a class="basecamp" href="map.html" style="color:#fff;text-decoration:none;margin-left:6px;">🗺️ Family Fun Map</a></div>',
)

# 3. Splice in the planner section before the "Closest to camp" section
marker = "  <!-- CLOSEST -->"
assert marker in html, "CLOSEST marker not found"
snippet = (repo / "planner_snippet.html").read_text(encoding="utf-8")
html = html.replace(marker, snippet + "\n\n" + marker, 1)

# 4. Emoji favicon
assert "</title>" in html
html = html.replace(
    "</title>",
    '</title>\n<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🏕️</text></svg>">',
    1,
)

(repo / "index.html").write_text(html, encoding="utf-8")
print("index.html written:", len(html), "bytes")
