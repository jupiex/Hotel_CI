with open("dashboard/board.html", encoding="utf-8") as f:
    html = f.read()

checks = [
    ("Leaflet CSS loaded",    "leaflet.css" in html),
    ("Leaflet JS loaded",     "leaflet.js" in html),
    ("Map div present",       "ci-map" in html),
    ("buildMarkets fn",       "buildMarkets" in html),
    ("initMap fn",            "initMap" in html),
    ("COORDS lookup",         "COORDS" in html),
    ("CartoDB dark tiles",    "carto" in html.lower()),
    ("Agent 1 entry",         "alerts_entry" in html),
    ("Agent 2 competitive",   "alerts_competitive" in html),
    ("Agent 6 regulatory",    "alerts_regulatory" in html),
    ("Legend present",        "map-legend" in html),
    ("Popup styles",          "pop-title" in html),
    ("A8 excluded caption",   "Agent 8" in html),
    ("Status colour RED",     "da3633" in html),
    ("Status colour YELLOW",  "d29922" in html),
    ("Status colour GREEN",   "2ea043" in html),
]

all_ok = True
for label, ok in checks:
    print(("OK  " if ok else "FAIL") + "  " + label)
    if not ok:
        all_ok = False

print()
print("All checks passed ✓" if all_ok else "SOME CHECKS FAILED ✗")
