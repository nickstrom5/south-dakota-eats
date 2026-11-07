"""South Dakota's open official records -> data/raw/official/ (git-ignored, never public).

Checked 2026-11-06 (playbook/12-sources.md). South Dakota has two inspection systems, both with official 0-100 scores: the Department of
Health's (statewide, search-only at sddoh.safefoodinspection.com, linked, never scraped) and the City of Sioux Falls' (inside city
limits), which the City publishes in bulk under CC BY 4.0:
- "Restaurant Sites" (gis.siouxfalls.gov Data/Safety/MapServer/17; ArcGIS item 67d60bc7760a4b3988f18685fd9898f6): one row per food
  service site with its two most recent inspection scores and dates (SCORE1/INSP_DATE1 the latest), the site type and a point. The layer
  doesn't say which visit was routine and which a follow-up.
- "Alcohol and Video Lottery Licensing" (Data/Community/MapServer/20; item f60df5268f3241e691789a6a33fe406b): license type, on- or
  off-sale, video lottery, business name and address, status. OwnerName is never requested.
One request at a time.
"""
import datetime, json, os, time
import requests

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "official")
os.makedirs(os.path.join(OUT, "siouxfalls"), exist_ok=True)
UA = "SouthDakotaEatsDataCheck/1.0 (+https://nickstrom5.github.io/south-dakota-eats/; nick@eatsranked.com)"
BASE = "https://gis.siouxfalls.gov/arcgis/rest/services/Data"
S = requests.Session(); S.headers["User-Agent"] = UA


def get(url, **params):
    for attempt in range(4):
        r = S.get(url, params=params, timeout=90)
        if r.status_code == 200:
            return r.json()
        time.sleep(5 * (attempt + 1))
    r.raise_for_status()


def arcgis(layer, fields, order="OBJECTID", page=1000, points=False):
    """Every row of a layer; with points, its point in WGS84 degrees (the layer's own LAT/LON fields are state-plane feet)."""
    rows, off = [], 0
    while True:
        d = get(f"{layer}/query", where="1=1", outFields=fields, returnGeometry="true" if points else "false", outSR=4326,
                orderByFields=order, resultOffset=off, resultRecordCount=page, f="json")
        feats = d.get("features") or []
        for f in feats:
            row = dict(f["attributes"])
            if points:
                g = f.get("geometry") or {}
                row["LAT"], row["LON"] = (g.get("y"), g.get("x")) if isinstance(g.get("y"), (int, float)) else (None, None)
            rows.append(row)
        if len(feats) < page and not d.get("exceededTransferLimit"):
            return rows
        off += len(feats)
        time.sleep(1)


TODAY = datetime.date.today().isoformat()
TERMS = "City of Sioux Falls open data, licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0)."
meta = {"siouxfalls": {"name": "City of Sioux Falls: Restaurant Sites (food inspections)", "url": f"{BASE}/Safety/MapServer/17",
                       "item": "https://www.arcgis.com/home/item.html?id=67d60bc7760a4b3988f18685fd9898f6", "fetched": TODAY, "terms": TERMS,
                       "cadence": "monthly"},
        "sf_liquor": {"name": "City of Sioux Falls: Alcohol and Video Lottery Licensing", "url": f"{BASE}/Community/MapServer/20",
                      "item": "https://www.arcgis.com/home/item.html?id=f60df5268f3241e691789a6a33fe406b", "fetched": TODAY, "terms": TERMS}}
sites = arcgis(f"{BASE}/Safety/MapServer/17",
               "OBJECTID,SITE_NO,INV_NO,SITE_INV,INV_TYPE,INSP_DATE1,INSP_DATE2,SCORE1,SCORE2,SITE_NAME,SITE_TYPE,SITE_TYPE_DESC,FULL_ADDRESS", points=True)
time.sleep(1)
lic = arcgis(f"{BASE}/Community/MapServer/20", "OBJECTID,On_OFF,VLT,VLT_Num,LicenseType,BusinessName,BusinessAddress,Status")
json.dump(sites, open(os.path.join(OUT, "siouxfalls", "restaurant_sites.json"), "w"))
json.dump(lic, open(os.path.join(OUT, "siouxfalls", "alcohol_licenses.json"), "w"))
json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), indent=1)
print("Sioux Falls restaurant sites:", len(sites), "| alcohol licenses:", len(lic))
