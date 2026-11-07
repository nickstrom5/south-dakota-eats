"""Writes data/research/app/*.json (hand-checked South Dakota guides), data/research/michelin.json, jbf.json and closed.json from the compact
lists below. Ported from nd-eats/pipeline/build_research.py.

Each entry cites the pages that name it, read on 2026-11-06: Experience Sioux Falls' own chislic guide, Visit Rapid City's own guide to
South Dakota foods (October 2024), and jamesbeard.org. The Argus Leader, KELO, Dakota News Now, SDPB and South Dakota Searchlight
disallow Claude in robots.txt and travelsouthdakota.com answers with a bot check, so none is cited. Readers' polls aren't used.
The address comes from the map listing we already hold for that name in that town (site/southdakota.json); a name that isn't found exactly
once in its town (or at the street number given) is left out and listed in data/research/app/LEADS.md.
Usage: ../.venv/bin/python build_research.py   (then southdakota.py)"""
import json, os, re, unicodedata
from brands import brand_of
from common import norm_name
ROOT = os.path.join(os.path.dirname(__file__), "..")
R = os.path.join(ROOT, "data", "research")
d = json.load(open(os.path.join(ROOT, "site", "southdakota.json")))
C, M = d["cols"], d["meta"]
# accents folded, apostrophes dropped
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", unicodedata.normalize("NFKD", (s or "").lower().replace("'", "").replace("’", ""))
                                             .encode("ascii", "ignore").decode())).strip()

ESF_CHISLIC = "https://www.experiencesiouxfalls.com/articles/where-to-get-the-best-chislic"               # Experience Sioux Falls (published 2020-06-19, updated 2026-02-26)
VRC_FOODS = "https://www.visitrapidcity.com/blog/post/popular-south-dakota-foods-you-have-to-try-and-where-to-find-them/"   # published 2024-10-29, updated 2025-05-22
JBF_AC24 = "https://www.jamesbeard.org/stories/announcing-the-2024-restaurant-and-chef-americas-classics-winners"          # 2024-02-27
JBF26 = "https://www.jamesbeard.org/stories/james-beard-award-semifinalists-2026"                       # 2026-01-21
JBF25 = "https://www.jamesbeard.org/stories/the-2025-james-beard-award-semifinalists"                   # 2025-01-22
SF, RC = "Sioux Falls", "Rapid City"
VRC = "Visit Rapid City"

GUIDES = {
 "chislic": [   # the state nosh (SDCL 1-6-16.10, 2018): cubes of lamb or beef, fried or grilled, on toothpicks
  ("The Alibi", SF, None, "A longtime neighborhood bar where chislic is a staple; the traditional lamb chislic is served Monday evenings "
   "(Experience Sioux Falls).", None, None, [ESF_CHISLIC]),
  ("The Barrel House", SF, None, "Seven ounces of hand-cut Prime beef chislic, breaded and country fried or seasoned and grilled "
   "(Experience Sioux Falls).", None, None, [ESF_CHISLIC]),
  ("The Attic Bar & Grill", SF, None, "Chislic as an appetizer or an entrée, on the southeast side (Experience Sioux Falls).", None, None,
   [ESF_CHISLIC]),
  ("Gateway Lounge", SF, "3408", "Eight ounces of top sirloin chislic (Experience Sioux Falls).", None, None, [ESF_CHISLIC]),
  ("Ode to Food & Drinks", SF, None, "Downtown: top sirloin chislic with chili peanut or ghost cheese sauce (Experience Sioux Falls).",
   None, None, [ESF_CHISLIC]),
  ("Tinner's Public House", SF, "449", "Beef or lamb chislic with Texas toast and celery (Experience Sioux Falls).", None, None, [ESF_CHISLIC]),
  ("Dakotah Steakhouse", RC, None, f"Chislic, bison, walleye and kuchen, all on {VRC}'s guide to South Dakota foods.", None, None, [VRC_FOODS]),
  ("Murphy's Pub & Grill", RC, None, f"Chislic and bison ({VRC}).", None, None, [VRC_FOODS]),
  ("Bokujo Ramen", RC, None, f"Chislic and bison ({VRC}).", None, None, [VRC_FOODS]),
  ("Paddy O'Neill's Irish Pub & Grill", RC, None, f"Chislic and walleye ({VRC}).", None, None, [VRC_FOODS]),
  ("The Park", RC, None, f"Chislic and walleye ({VRC}).", None, None, [VRC_FOODS]),
  ("Thirsty's", RC, None, f"Chislic, bison and fry bread ({VRC}).", None, None, [VRC_FOODS]),
  ("The Pheasant Restaurant & Lounge", "Brookings", None, "The James Beard Foundation's 2024 America's Classic: it opened in 1949 as a gas "
   "station café, and its chislic is lamb from a local ranch.", 1949, "James Beard Foundation (2024): it opened in 1949 as a gas station café.",
   [JBF_AC24])],
 "bison walleye": [   # Rapid City, from the visitor bureau's own guide
  ("Tally's Silver Spoon", RC, None, f"Bison, on {VRC}'s guide to South Dakota foods.", None, None, [VRC_FOODS]),
  ("Colonial House", RC, None, f"Bison and walleye, and kuchen some days ({VRC}).", None, None, [VRC_FOODS]),
  ("Delmonico Grill", RC, None, f"Bison ({VRC}).", None, None, [VRC_FOODS]),
  ("Firehouse Brewing Company", RC, "610", f"Bison ({VRC}).", None, None, [VRC_FOODS]),
  ("Shipwrecks Bar & Grill", RC, None, f"Walleye ({VRC}).", None, None, [VRC_FOODS]),
  ("Bashful Bison", RC, None, f"Bison ({VRC}).", None, None, [VRC_FOODS]),
  ("Dakotah Steakhouse", RC, None, f"Bison, walleye and chislic ({VRC}).", None, None, [VRC_FOODS]),
  # the same Visit Rapid City guide (updated May 2025) names these for bison or walleye too
  ("Murphy's Pub & Grill", RC, None, f"Chislic and bison ({VRC}).", None, None, [VRC_FOODS]),
  ("Bokujo Ramen", RC, None, f"Chislic and bison ({VRC}).", None, None, [VRC_FOODS]),
  ("Paddy O'Neill's Irish Pub & Grill", RC, None, f"Chislic and walleye ({VRC}).", None, None, [VRC_FOODS]),
  ("The Park", RC, None, f"Chislic and walleye ({VRC}).", None, None, [VRC_FOODS]),
  ("Thirsty's", RC, None, f"Chislic, bison and fry bread ({VRC}).", None, None, [VRC_FOODS]),
  ("The Wine Cellar", RC, None, f"Bison ({VRC}).", None, None, [VRC_FOODS]),             # its listing: 513 6th Street
  ("Enigma", RC, None, f"Bison, at the Rushmore Hotel ({VRC}).", None, None, [VRC_FOODS])],   # its listing: 445 Mount Rushmore Road
 "oldest": [],
}
ADDR = {}
CUISINE = {}
KINDS = {k: [k] for k in ("chislic", "bison walleye", "oldest")}

# MICHELIN: no guide covers South Dakota (guide.michelin.com/us/en/south-dakota/restaurants answered 404 in September 2026)
MICHELIN = []
MI_MATCH = {}
MI_UT = None
MID = "Best Chef: Midwest"
JBF = [{"name": "The Pheasant Restaurant & Lounge", "city": "Brookings", "honors": ["America's Classics 2024"], "sources": [JBF_AC24]},
       {"name": "Hjem A.M.", "city": "Custer", "honors": [f"{MID} semifinalist 2026 (Camillia and Erik Hjortnaes)"], "sources": [JBF26]},
       {"name": "Skogen Kitchen", "city": "Custer", "honors": [f"{MID} semifinalist 2025 (Joseph Raney)"], "sources": [JBF25]},
       {"name": "BibiSol", "city": SF, "honors": ["Emerging Chef semifinalist 2025 (Marcela Salas)"], "sources": [JBF25]},
       {"name": "CH Patisserie", "city": SF, "honors": ["Outstanding Pastry Chef or Baker semifinalist 2025 (Chris Hanmer)"], "sources": [JBF25]}]
CLOSED = []


def key(s):
    """The name key without a leading "the": "Varsity" is our "The Varsity"."""
    return re.sub(r"\s+", " ", re.sub(r"\band\b", " ", re.sub(r"^the ", "", norm(s)))).strip()   # "Don & Millie's" is "Don and Millies"


def find(name, town, num):
    k = key(name)
    hits = [i for i, n in enumerate(C["name"]) if C["city"][i] is not None and M["cities"][C["city"][i]] == town
            and (key(n) == k or key(n).startswith(k + " ") or k.startswith(key(n) + " ") or key(n).replace(" ", "") == k.replace(" ", "")
                 or (key(n).split()[:2] == k.split()[:2] and len(k.split()) >= 2)
                 # a street number checked by hand on the source's own listing: the first word is enough ("Gateway Lounge" at 3408 Gateway
                 # Blvd is Overture's "Gateway Casino & Lounge"; "Firehouse Brewing Company" at 610 Main St its "Firehouse Brewery & Restaurant")
                 or (num and key(n).split()[:1] == k.split()[:1]))]
    if num:
        hits = [i for i in hits if (C["addr"][i] or "").split(" ")[0] == num]
    return hits


leads, n_out = [], {}
for kind, rows in GUIDES.items():
    out = []
    for name, town, num, note, founded, fnote, srcs in rows:
        hits = find(name, town, num)
        if not hits and (name, town) in ADDR:
            out.append({"name": name, "address": ADDR[(name, town)], "city": town, "zip": None, "kinds": KINDS[kind], "dishes": [], "note": note,
                        "founded": founded, "founded_note": fnote, "website": None, "open": True, "evidence_date": "2026-10",
                        "sources": srcs, "match_names": []} | ({"cuisine": CUISINE[(name, town)]} if (name, town) in CUISINE else {}))
            continue
        if len(hits) != 1:
            leads.append(f"- {kind}: {name} ({town}{', ' + num if num else ''}) — {len(hits)} matches in our data; not added"); continue
        i = hits[0]
        out.append({"name": C["name"][i], "address": C["addr"][i], "city": town, "zip": str(C["zip"][i]) if C["zip"][i] else None,
                    "kinds": KINDS[kind], "dishes": [], "note": note, "founded": founded, "founded_note": fnote, "website": None, "open": True,
                    "evidence_date": "2026-10", "sources": srcs, "match_names": [name.upper()] if norm(name) != norm(C["name"][i]) else []})
        if brand_of(norm_name(name)):   # a chain shows under its own spelling at every branch, whatever the listing says
            out[-1]["display"] = name
        if (name, town) in CUISINE:
            out[-1]["cuisine"] = CUISINE[(name, town)]
    fn = re.sub(r"[^a-z]+", "_", kind).strip("_")
    json.dump(out, open(f"{R}/app/{fn}.json", "w"), indent=1, ensure_ascii=False)
    n_out[kind] = len(out)

MI_ADDR = {}
json.dump({"restaurants": [{"name": n, "address": MI_ADDR.get(n), "city": t, "zip": None, "distinction": dist, "cuisine": cu, "green_star": False,
                             "michelin_url": MI_UT, "sources": [MI_UT], "match_names": [x.upper() for x in MI_MATCH.get(n, [])], "open": True}
                            for n, t, dist, cu in MICHELIN]}, open(f"{R}/michelin.json", "w"), indent=1, ensure_ascii=False)
json.dump([dict({"address": None}, **j, zip=None, open=True) for j in JBF], open(f"{R}/jbf.json", "w"), indent=1, ensure_ascii=False)
json.dump(CLOSED, open(f"{R}/closed.json", "w"), indent=1, ensure_ascii=False)
open(f"{R}/app/LEADS.md", "w").write("# South Dakota research leads (not yet verified)\n\nWritten by pipeline/build_research.py.\n\n" + "\n".join(leads) + """

## Waiting for a source we may use, or for the map data
- Chislic in the Chislic Circle: Papa's (Freeman) and Meridian Corner have only South Dakota Magazine's 2012 story and SiouxFalls.Business
  pages from before 2025; Urban Chislic (Sioux Falls) closed in August 2024.
- Indian tacos and frybread: Laughing Water Restaurant at Crazy Horse Memorial (its Visit Rapid City listing answered 404) and Malissa's
  Frybread (a food truck; its listing shows no text); Thirsty's (Rapid City) has fry bread per Visit Rapid City (updated May 2025). Native ownership
  needs the business's or tribe's own word.
- Kuchen: Tyndall Bakery, the Eureka Kuchen Factory and Pietz's Kuchen Kitchen (Scotland) have South Dakota Magazine pages without a
  2025-26 date; Dakotah Steakhouse (Rapid City) serves kuchen per Visit Rapid City (updated May 2025).
- Oldest: Wall Drug's café (1931 at this address?) needs a dated source tying the year to the café.
- Blocked or unusable hosts: argusleader.com, keloland.com, dakotanewsnow.com, sdpb.org, southdakotasearchlight.com, mitchellrepublic.com,
  yankton.net, aberdeennews.com, brookingsregister.com and capjournal.com disallow Claude; travelsouthdakota.com answers with a bot check.
- Official data: the Department of Health's inspections (sddoh.safefoodinspection.com) are search-only; an export request is Nick's call.
""")
print(n_out, "| leads:", len(leads))
for l in leads: print(l)
