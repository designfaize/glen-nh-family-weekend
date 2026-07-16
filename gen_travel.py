"""Generate travel.json: a place-to-place drive-time matrix (minutes) for every
location used by the itinerary builder. Uses the public OSRM demo server once at
build time; falls back to a road-factor haversine estimate if OSRM is down.
Location order here must match the LOC mapping in planner_snippet.html."""
import json
import math
import pathlib
import urllib.request

# (name, lat, lon) — approximate is fine; OSRM snaps to the nearest road.
LOCS = [
    ("Jellystone camp", 44.1000, -71.1920),        # 0
    ("Story Land / Living Shores", 44.1080, -71.1820),  # 1
    ("Cranmore", 44.0526, -71.1120),               # 2
    ("Diana's Baths", 44.0745, -71.1620),          # 3
    ("Conway Scenic RR", 44.0537, -71.1284),       # 4
    ("Echo Lake", 44.0585, -71.1509),              # 5
    ("Kanc Lower Falls", 44.0000, -71.2360),       # 6
    ("Auto Road / Great Glen", 44.2876, -71.2306), # 7
    ("Jackson Falls", 44.1450, -71.1840),          # 8
    ("Glen Ellis Falls", 44.2540, -71.2530),       # 9
    ("Santa's Village", 44.4229, -71.4409),        # 10
    ("Cog Railway", 44.2695, -71.3509),            # 11
    ("Clark's Bears", 44.0684, -71.6811),          # 12
    ("Whale's Tale", 44.0806, -71.6773),           # 13
    ("Alpine Adventures", 44.0461, -71.6819),      # 14
    ("Flume Gorge", 44.0977, -71.6811),            # 15
    ("Lost River", 44.0384, -71.7772),             # 16
    ("Funspot", 43.6118, -71.4644),                # 17
    ("Gunstock", 43.5384, -71.3634),               # 18
    ("Weirs Beach", 43.6067, -71.4630),            # 19
    ("Settlers Green", 44.0397, -71.1198),         # 20
    ("Red Parka", 44.1000, -71.1911),              # 21
    ("Cider Co", 44.1030, -71.1863),               # 22
    ("Almost There Tavern", 44.0980, -71.2050),    # 23
    ("Muddy Moose", 44.0446, -71.1246),            # 24
    ("Moat Mountain", 44.0672, -71.1322),          # 25
    ("May Kelly's", 44.0575, -71.1290),            # 26
    ("Delaney's", 44.0561, -71.1288),              # 27
    ("Flatbread", 44.0520, -71.1280),              # 28
    ("Banners", 43.9850, -71.1160),                # 29
    ("Priscilla's", 44.0480, -71.1260),            # 30
    ("Peach's", 44.0470, -71.1255),                # 31
    ("Zeb's", 44.0530, -71.1282),                  # 32
    ("Hart's Turkey Farm", 43.6440, -71.4990),     # 33
    ("Woodstock Inn", 44.0324, -71.6853),          # 34
    ("Dunkin' Glen", 44.1080, -71.1825),           # 35
    ("McDonald's", 44.0335, -71.1185),             # 36
    ("Five Guys", 44.0310, -71.1170),              # 37
    ("Taco Bell", 44.0320, -71.1175),              # 38
    ("Burger King", 44.0250, -71.1150),            # 39
    ("Subway", 44.0280, -71.1160),                 # 40
    ("Wendy's Gilford", 43.5867, -71.4256),        # 41
    ("Kahuna Laguna", 44.0430, -71.1250),          # 42
    ("Attitash", 44.0827, -71.2290),               # 43
    ("Chutters Littleton", 44.3061, -71.7701),     # 44
    ("Pirate's Cove N Conway", 44.0400, -71.1200), # 45
    ("Saco Bound tubing", 43.9905, -71.0570),      # 46
    ("MWV Children's Museum", 44.0560, -71.1288),  # 47
    ("Gorham moose tour", 44.3879, -71.1730),      # 48
    ("Polar Caves", 43.7570, -71.7290),            # 49
    ("Squam Lakes Science Ctr", 43.7320, -71.5880),# 50
    ("Home — Middleton MA", 42.5940, -71.0160),    # 51
]


def haversine_min(a, b):
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, (a[1], a[2], b[1], b[2]))
    d = 2 * R * math.asin(math.sqrt(
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    ))
    return max(1, round(d * 1.35 / 50 * 60))  # 1.35 road factor, 50 km/h avg


def osrm_matrix():
    coords = ";".join(f"{lon},{lat}" for _, lat, lon in LOCS)
    url = f"https://router.project-osrm.org/table/v1/driving/{coords}?annotations=duration"
    with urllib.request.urlopen(url, timeout=60) as r:
        data = json.loads(r.read())
    if data.get("code") != "Ok":
        raise RuntimeError(data.get("code"))
    return [
        [max(1, round((s or 0) / 60)) if i != j else 0 for j, s in enumerate(row)]
        for i, row in enumerate(data["durations"])
    ]


try:
    matrix = osrm_matrix()
    source = "osrm"
except Exception as e:
    print("OSRM failed (%s) — falling back to haversine estimates" % e)
    matrix = [
        [0 if i == j else haversine_min(a, b) for j, b in enumerate(LOCS)]
        for i, a in enumerate(LOCS)
    ]
    source = "haversine"

# Calibrate: OSRM's demo profile runs slow on rural NH roads. Pin every camp leg
# to the guide's published drive times, and scale all other pairs by the median
# guide/OSRM ratio so hop times feel consistent with the chips.
CAMP_KNOWN = {
    1: 3, 2: 15, 3: 15, 4: 12, 5: 15, 6: 15, 7: 20, 8: 12, 9: 20,
    10: 45, 11: 40, 12: 50, 13: 50, 14: 50, 15: 55, 16: 55,
    17: 75, 18: 75, 19: 75, 20: 12,
    21: 4, 22: 3, 23: 3, 24: 12, 25: 12, 26: 13, 27: 12, 28: 12,
    29: 15, 30: 12, 31: 12, 32: 12, 33: 65, 34: 55,
    35: 3, 36: 12, 37: 13, 38: 12, 39: 11, 40: 12, 41: 80,
    42: 12, 43: 8, 44: 50, 45: 12, 46: 18, 47: 12, 48: 35, 49: 70, 50: 60,
    51: 145,
}
ratios = sorted(CAMP_KNOWN[i] / matrix[0][i] for i in CAMP_KNOWN if matrix[0][i])
scale = ratios[len(ratios) // 2]
print(f"calibration scale (median guide/OSRM): {scale:.2f}")
n = len(LOCS)
for i in range(n):
    for j in range(n):
        if i == j:
            continue
        if i == 0:
            matrix[i][j] = CAMP_KNOWN.get(j, matrix[i][j])
        elif j == 0:
            matrix[i][j] = CAMP_KNOWN.get(i, matrix[i][j])
        else:
            matrix[i][j] = max(1, round(matrix[i][j] * scale))

out = pathlib.Path(__file__).parent / "travel.json"
out.write_text(json.dumps({"source": source, "matrix": matrix}), encoding="utf-8")
print(f"travel.json written ({source}), {len(LOCS)}x{len(LOCS)}")
for a, b in [(0, 2), (0, 17), (2, 29), (0, 1), (17, 41)]:
    print(f"  {LOCS[a][0]} -> {LOCS[b][0]}: {matrix[a][b]} min")
