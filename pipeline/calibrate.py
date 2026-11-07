"""How often is a map listing a real food or drink business? -> data/sd/calibration*.json

Ported from ut-eats/pipeline/calibrate.py (co-eats -> tx-eats -> az-eats -> tn-eats -> ga-eats -> la-eats -> md-eats). South Dakota's one
official list a script may read is the City of Sioux Falls' food service sites (playbook/12-sources.md), so the measure is the share
of each kind of Sioux Falls listing found on it. No Google data is read for South Dakota, so the 2021 share is empty. The keep rule is the
family's (Meta 0.95, or 0.90 with a website), measured in the states that have lists. This script also gives every listing and license its county.
"""
import json
import numpy as np, pandas as pd
from shapely.geometry import shape, Point
from shapely import STRtree
from common import SD
from listings_util import official_match
import official

o = pd.read_pickle(f"{SD}/stage1.pkl")
F = pd.read_pickle(f"{SD}/official.pkl")
_CN = json.load(open(f"{SD}/sd_counties_detail.geojson"))
_NAMES = list(_CN)
_RAW = [shape(_CN[n]) for n in _NAMES]
_GEOMS = [g.buffer(0.0003) for g in _RAW]
_TREE = STRtree(_GEOMS)


def county_of(la, lo):
    """The county the point is in, by its own outline first (the ~30 m buffers overlap along every county line; in Maryland a
    Takoma Park pin 20 m inside Montgomery came out as Prince George's); a pin just over a lake shore (Antelope Island, Bear Lake, Lake
    Powell's marinas) takes the nearest county within ~1 km."""
    if la != la:
        return None
    p = Point(lo, la)
    hits = [i for i in _TREE.query(p) if _GEOMS[i].contains(p)]
    exact = [i for i in hits if _RAW[i].contains(p)]
    if exact or hits:
        return _NAMES[(exact or hits)[0]]
    near = [(_GEOMS[i].distance(p), _NAMES[i]) for i in _TREE.query(p.buffer(0.01))]
    return min(near)[1] if near else None


o["county"] = [county_of(la, lo) for la, lo in zip(o.lat, o.lon)]
F["county"] = [county_of(la, lo) for la, lo in zip(F.lat, F.lon)]
o.to_pickle(f"{SD}/stage1.pkl")
F.to_pickle(f"{SD}/official.pkl")

base = ~o.j_junk & ~o.j_outside
print("listings with a county:", int(o.county.notna().sum()), "of", len(o), "| licenses placed:", int(F.lat.notna().sum()), "of", len(F))


def groups(L, app=False):
    s = L.src.fillna("none")
    if app:
        conf = L.confidence.fillna(0)
        has_web = L.n_web.fillna(0).astype(int) > 0
        return np.select([L.ov_closed | L.j_closedname, (s == "meta") & (conf >= 0.95), (s == "meta") & (conf >= 0.9) & has_web,
                          (s == "meta") & (conf >= 0.9), s.isin(["AllThePlaces", "DAC"]), (s == "BrightQuery") & (conf >= 0.95), s == "meta"],
                         ["closed per Overture/name", "meta_high", "meta_mid_web", "meta_mid_noweb", "brand_feed", "bq_high", "meta_low"],
                         "other_sources")
    return np.select([L.closed21, L.ov_closed, (s == "meta") & L.in21, s == "meta", s.isin(["AllThePlaces", "DAC"]) & L.in21,
                      s.isin(["AllThePlaces", "DAC"]), L.in21, s == "Foursquare", s == "BrightQuery", s == "Microsoft"],
                     ["Google 2021 says closed", "Overture says closed", "Meta + open in Google 2021", "Meta only",
                      "brand feed + Google 2021", "brand feed only", "Foursquare/BrightQuery/Microsoft + Google 2021",
                      "Foursquare only", "BrightQuery only", "Microsoft only"], "other")


def measure(label, L, R, store_web, store_app, by_county=True):
    L = L.reset_index(drop=True)
    R = R.reset_index(drop=True)
    m = {}
    if by_county:   # "100 Main St" is in dozens of towns: match inside one county
        for cty, idx in L.groupby("county").groups.items():
            Rc = R[R.county == cty]
            if not len(Rc):
                continue
            Lc = L.loc[idx].reset_index()
            for i, j in official_match(Lc, Rc.reset_index(drop=True)).items():
                m[int(Lc.at[i, "index"])] = int(Rc.index[j])
    else:
        m = official_match(L, R)
    L["hit"] = L.index.map(lambda i: i in m)
    for mode, store in ((False, store_web), (True, store_app)):
        L["grp"] = groups(L, mode)
        t = L.groupby("grp").agg(n=("id", "size"), official=("hit", "mean"), open21=("in21", "mean")).sort_values("n", ascending=False)
        print(f"\n== {label} ({'app grouping' if mode else 'web grouping'}): {len(L)} listings, {len(R)} official records")
        print(t.assign(official=(t.official * 100).round(1), open21=(t.open21 * 100).round(1)).to_string())
        store[label] = {"listings": int(len(L)), "official_records": int(len(R)),
                        "groups": {g: {"n": int(r.n), "official": round(float(r.official), 3)} for g, r in t.iterrows()}}
    keepish = ~(L.ov_closed | L.j_closedname | L.closed21)
    got = set(R.biz.iloc[[m[i] for i in L.index[keepish] if i in m]])
    Rr = R[R.kind.eq("food")].drop_duplicates("biz")
    cover = float(np.mean([b in got for b in Rr.biz])) if len(Rr) else None
    print(f"{label}: official food businesses found among open map listings: {cover * 100:.1f}% of {len(Rr)}")
    store_web[label]["coverage"] = round(cover, 3)
    store_web[label]["official_food"] = int(len(Rr))


res, app = {}, {}
# Sioux Falls is the one official list: how many of each kind of listing in the city are on the City's food service list
_mp = o[base & o.city.eq("Sioux Falls")]
_R = F[F.jur.eq("siouxfalls") & F.active & F.kind.eq("food")].copy()
measure("Sioux Falls", _mp, _R, res, app)

# the share Google 2021 still showed open, statewide, per app group (a listing Google had in 2021 and didn't call closed)
L = o[base].copy()
L["grp"] = groups(L, True)
L["open21"] = L.in21 & ~L.closed21
g21 = L.groupby("grp").open21.agg(["size", "mean"])
print("\n== open in Google 2021 (statewide, app grouping)\n" + (g21.assign(mean=(g21["mean"] * 100).round(1))).to_string())
# the app ships no Google-derived number, so calibration_app.json leaves the 2021 share out (calibration.json, read only by the
# private leaderboard, keeps it), as in sc-eats

per = o[base & o.county.notna() & ~o.ov_closed & ~o.j_closedname].groupby("county").size()
print("\n== open, cleaned listings per county (top 15)\n" + per.sort_values(ascending=False).head(15).to_string())
json.dump({"areas": res, "per_county_listings": {c: int(n) for c, n in per.items()},
           "open_google_2021": {g: {"n": int(r["size"]), "share": round(float(r["mean"]), 3)} for g, r in g21.iterrows()}},
          open(f"{SD}/calibration.json", "w"), indent=1)
json.dump(app, open(f"{SD}/calibration_app.json", "w"), indent=1)
