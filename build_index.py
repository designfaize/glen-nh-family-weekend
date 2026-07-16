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

# 6a. Pamphlet-rack classics section before the restaurants
CLASSICS = """  <!-- PAMPHLET CLASSICS -->
  <section>
    <h2><span class="em">🎪</span> The pamphlet-rack classics</h2>
    <p class="sub">Every lobby up here has a wall of brochures — these are the ones worth grabbing: indoor water, candy by the foot, tube floats, caves, and moose.</p>
    <div class="grid">
      <div class="card"><div class="tag coaster">🎢 Alpine slide · Coaster</div><h3><a href="https://www.attitash.com/" target="_blank" rel="noopener">Attitash Mountain Resort</a></h3><span class="drive">🚗 8 min · Bartlett</span><p>North America's <b>longest alpine slide</b> plus the Nor'easter mountain coaster, waterslides, airbag jump, and a scenic chairlift — the closest big adventure park to camp.</p></div>
      <div class="card"><div class="tag rain">💦 Indoor waterpark</div><h3><a href="https://www.kahunalaguna.com/" target="_blank" rel="noopener">Kahuna Laguna</a></h3><span class="drive">🚗 12 min</span><p>40,000 sq ft of indoor slides, wave pool, and a giant tipping bucket at the Red Jacket resort. Day passes for non-guests <b>when space allows — call ahead</b>. The ultimate rainy-day splash.</p></div>
      <div class="card"><div class="tag eat">🍭 Candy · Road trip</div><h3><a href="https://www.chutters.com/" target="_blank" rel="noopener">Chutters — Littleton</a></h3><span class="drive far">🚗 ~50 min</span><p>Home of the <b>world's longest candy counter</b> — 112 feet of jars. Pairs perfectly with a Santa's Village day (Littleton is ~20 min past Jefferson).</p></div>
      <div class="card"><div class="tag">⛳ Mini golf</div><h3>Pirate's Cove — North Conway</h3><span class="drive">🚗 12 min</span><p>The classic pirate-ship mini golf on the strip — caves, waterfalls, and 18 holes of family rivalry.</p></div>
      <div class="card"><div class="tag wet">🛶 River float</div><h3><a href="https://www.sacobound.com/" target="_blank" rel="noopener">Saco River tubing — Saco Bound</a></h3><span class="drive">🚗 18 min</span><p>Lazy tube floats and canoe trips on the warm, sandy-bottomed Saco out of Center Conway, shuttle included.</p></div>
      <div class="card"><div class="tag rain">☔ Little kids</div><h3><a href="https://www.mwvchildrensmuseum.org/" target="_blank" rel="noopener">MWV Children's Museum</a></h3><span class="drive">🚗 12 min</span><p>Hands-on play museum in North Conway village — a great under-8 rainy morning.</p></div>
      <div class="card"><div class="tag trail">🌲 Moose safari</div><h3>Gorham moose tours</h3><span class="drive far">🚗 ~35 min · evenings</span><p>Evening van tours up in the North Country with famously high moose-spotting rates. Book ahead — kids never forget their first moose.</p></div>
      <div class="card"><div class="tag rain">🦇 Caves</div><h3><a href="https://polarcaves.com/" target="_blank" rel="noopener">Polar Caves Park — Rumney</a></h3><span class="drive far">🚗 ~1 hr 10</span><p>Boardwalk trails through nine glacial caves you squeeze and duck through — right off I‑93 on the drive home.</p></div>
      <div class="card"><div class="tag trail">🦉 Wildlife</div><h3><a href="https://nhnature.org/" target="_blank" rel="noopener">Squam Lakes Science Center</a></h3><span class="drive far">🚗 ~1 hr</span><p>Live black bears, bobcats, and otters along a woodland trail, plus lake cruises — "On Golden Pond" territory, near the drive home.</p></div>
    </div>
  </section>

"""
rest_marker = "  <!-- RESTAURANTS -->"
assert rest_marker in html, "restaurants marker not found"
html = html.replace(rest_marker, CLASSICS + rest_marker, 1)

# 6b. Inject the place-to-place drive-time matrix (regenerate with gen_travel.py)
import json

travel = json.loads((repo / "travel.json").read_text(encoding="utf-8"))

# 6b2. Extra indoor cards in the "If it rains" section
rainy_anchor = '<div class="card"><div class="tag rain">Indoor</div><h3><a href="https://www.funspotnh.com/" target="_blank" rel="noopener">Funspot arcade</a></h3>'
assert rainy_anchor in html, "rainy Funspot card not found"
html = html.replace(
    rainy_anchor,
    '<div class="card"><div class="tag rain">Indoor · Waterpark</div><h3><a href="https://www.kahunalaguna.com/" target="_blank" rel="noopener">Kahuna Laguna</a></h3><span class="drive">🚗 12 min</span><p>The 40,000 sq ft indoor waterpark — call ahead for non-guest day passes.</p></div>\n'
    '      <div class="card"><div class="tag rain">Indoor · Laser tag</div><h3>Uberblast — North Conway</h3><span class="drive">🚗 12 min</span><p>Indoor laser tag, arcade, and gaming near Settlers Green — the kid-approved rain fix.</p></div>\n'
    '      <div class="card"><div class="tag rain">Indoor · Bowling</div><h3>Saco Valley Sports Center</h3><span class="drive">🚗 ~18 min · Fryeburg</span><p>Candlepin bowling with bumpers, golf simulators, air hockey, and pool tables just over the Maine line.</p></div>\n'
    "      " + rainy_anchor,
    1,
)

# 6c. Trip weather section (animated forecast cards) before the itinerary
wx_marker = "  <!-- ITINERARY -->"
assert wx_marker in html, "itinerary marker not found"
wx = (repo / "weather_snippet.html").read_text(encoding="utf-8")
html = html.replace(wx_marker, wx + "\n\n" + wx_marker, 1)

# 7. Splice in the planner section before the "Closest to camp" section
marker = "  <!-- CLOSEST -->"
assert marker in html, "CLOSEST marker not found"
snippet = (repo / "planner_snippet.html").read_text(encoding="utf-8")
travel_marker = "var TRAVEL=null;/*__TRAVEL__*/"
assert travel_marker in snippet, "TRAVEL marker not found in snippet"
snippet = snippet.replace(
    travel_marker,
    "var TRAVEL=" + json.dumps(travel["matrix"], separators=(",", ":"))
    + ";var COORDS=" + json.dumps(travel["locs"], separators=(",", ":")) + ";",
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
