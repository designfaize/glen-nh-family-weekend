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

# 3. Remove the fallback schedule table under the live calendar
start = html.index('<p class="sub" style="margin-top:20px;">If the live calendar doesn')
end = html.index("</div>", html.index("</table>", start)) + len("</div>")
html = html[:start] + html[end:]

# ...and the now-dangling reference to it
old_ref = "tap <b>“Open the live calendar”</b> or use the printable list further down."
assert old_ref in html, "calendar fallback reference not found"
html = html.replace(old_ref, "tap <b>“Open the live calendar”</b>.")

# 4. Static day cards -> dynamic container rendered from the builder state
start = html.index('<div class="day">')
end = html.index('<div class="note">')
assert start < end, "day cards not where expected"
html = html[:start] + '<div id="dyn-days"></div>\n\n    ' + html[end:]

old_sub = (
    '<p class="sub">Built around Jellystone. Mix and match — nothing here is locked in. '
    "Mornings out, afternoons flexible (parks get hot; the campground pool is a great reset).</p>"
)
assert old_sub in html, "plan sub text not found"
html = html.replace(
    old_sub,
    '<p class="sub">This plan writes itself from your picks in the <a href="#builder">itinerary builder below</a> — '
    "drag things in down there and each day fills in up here. Friday check-in and the Monday rollout stay put.</p>",
)

# 5. Funspot detour callout in the "On the way home" box
old_funspot = "aim to stop on the drive up or the drive home.</b>"
assert old_funspot in html, "funspot sentence not found"
html = html.replace(
    old_funspot,
    old_funspot
    + " Figure about <b>35–40 minutes of total detour time</b> — worth it to visit the biggest arcade on the planet? <b>Yes.</b>",
)

# 6. Fast food & quick bites group at the end of the eats section
FAST_FOOD = """
    <h3 style="margin:20px 0 2px;color:var(--pine);font-size:17px;">Fast food &amp; quick bites</h3>
    <div class="grid">
      <div class="card"><div class="tag eat">🍩 Coffee · Donuts</div><h3><a href="https://locations.dunkindonuts.com/en/nh/glen/850-nh-route-16/354716" target="_blank" rel="noopener">Dunkin' — Glen</a></h3><span class="drive">🚗 3 min · Glen</span><p>Right on Rt 16 in Glen — the morning coffee-and-Munchkins run before the parks (second location a few minutes south in Bartlett).</p></div>
      <div class="card"><div class="tag eat">🍟 Fast food</div><h3><a href="https://www.mcdonalds.com/us/en-us/location/nh/north-conway/1750-white-mountain-hwy/1952.html" target="_blank" rel="noopener">McDonald's — North Conway</a></h3><span class="drive">🚗 12 min</span><p>1750 White Mountain Hwy, right on the strip. The zero-negotiation option after a long park day.</p></div>
      <div class="card"><div class="tag eat">🍔 Burgers · Fries</div><h3>Five Guys — North Conway</h3><span class="drive">🚗 12 min</span><p>1623 White Mountain Hwy — a step-up burger and a mountain of fries, same strip.</p></div>
      <div class="card"><div class="tag eat">🌮 Tacos</div><h3>Taco Bell — North Conway</h3><span class="drive">🚗 12 min</span><p>1672 White Mountain Hwy, next to everything else on the strip.</p></div>
      <div class="card"><div class="tag eat">🍔 Fast food</div><h3>Burger King — North Conway</h3><span class="drive">🚗 12 min</span><p>1385 White Mountain Hwy, on the way into town from Glen.</p></div>
      <div class="card"><div class="tag eat">🥪 Subs</div><h3>Subway — North Conway</h3><span class="drive">🚗 12 min</span><p>1500 White Mountain Hwy — grab subs for a Kancamagus or Echo Lake picnic.</p></div>
      <div class="card"><div class="tag eat">🥤 Frosty run</div><h3><a href="https://locations.wendys.com/united-states/nh/gilford" target="_blank" rel="noopener">Wendy's — nearest: Gilford</a></h3><span class="drive far">🚗 ~1 hr 15 · by Funspot</span><p>Heads-up: North Conway's Wendy's closed (a new one near Settlers Green is approved but not open yet). Closest today is 1428 Lake Shore Rd in Gilford — about 10 min from Funspot — with another off I‑93 in Tilton. Pair the Frosty with the arcade stop on the drive home.</p></div>
    </div>
"""
eats_end = "  </section>\n\n  <!-- RAINY DAY -->"
assert eats_end in html, "eats section end not found"
html = html.replace(eats_end, FAST_FOOD + eats_end, 1)

# 6b. Inject the place-to-place drive-time matrix (regenerate with gen_travel.py)
import json

travel = json.loads((repo / "travel.json").read_text(encoding="utf-8"))

# 7. Splice in the planner section before the "Closest to camp" section
marker = "  <!-- CLOSEST -->"
assert marker in html, "CLOSEST marker not found"
snippet = (repo / "planner_snippet.html").read_text(encoding="utf-8")
travel_marker = "var TRAVEL=null;/*__TRAVEL__*/"
assert travel_marker in snippet, "TRAVEL marker not found in snippet"
snippet = snippet.replace(
    travel_marker,
    "var TRAVEL=" + json.dumps(travel["matrix"], separators=(",", ":")) + ";",
)
html = html.replace(marker, snippet + "\n\n" + marker, 1)

# 8. Emoji favicon
assert "</title>" in html
html = html.replace(
    "</title>",
    '</title>\n<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🏕️</text></svg>">',
    1,
)

(repo / "index.html").write_text(html, encoding="utf-8")
print("index.html written:", len(html), "bytes")
