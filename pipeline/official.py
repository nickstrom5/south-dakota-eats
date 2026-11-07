"""Official records for South Dakota -> one table of licensed food businesses (playbook/12-sources.md).
- The City of Sioux Falls inspects food service inside city limits and publishes its "Restaurant Sites" layer under CC BY 4.0: each site's
  two most recent inspection scores (the City's own 0-100) and dates. Shown as the City publishes them, dated; never a grade of ours.
  The layer doesn't say which visit was routine and which a follow-up, so neither is labeled.
- The rest of the state is the Department of Health's (search-only at sddoh.safefoodinspection.com; linked, never scraped).
- Alcohol: the City's "Alcohol and Video Lottery Licensing" layer (CC BY 4.0): license code, on- or off-sale, status. Owner names are
  never read. Cities and counties license alcohol elsewhere, with no statewide list, so "Serves alcohol" is unknown outside Sioux Falls.

load() returns one table: jur, lic (our id), name, keys (name keys), addr, city, zip, num, street, lat, lon, kind, active, ltype, insp,
biz.
"""
import os, re, json, datetime
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd
from common import norm_name, RAW, name_sim, _stems, GENERIC, canon_city

OFF = os.path.join(RAW, "official")
DIRS = {"N": "N", "S": "S", "E": "E", "W": "W", "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W"}
TYPES = set("ST STREET AVE AV AVENUE BLVD BOULEVARD RD ROAD DR DRIVE LN LANE CT COURT PL PLACE PKWY PARKWAY TER TRL TRAIL WAY HWY CIR "
            "CIRCLE PLZ SQ MALL BND PASS XING RUN ROW WALK RDG LOOP FWY FREEWAY EXPY EXPRESSWAY PIKE PK PKE".split())


def road(a):
    """One spelling for numbered roads. South Dakota writes one road as 'Route 100', 'US 7', 'Rt 2', 'SD 100' or 'SD Route 100', so every
    numbered US or state route is 'SH n' (as in ri-eats); 'N INTERSTATE 95' = 'I-95'; 'COUNTY ROAD 5' = 'CR 5'."""
    a = re.sub(r"(\d)\s*&\s*(\d)", r"\1-\2", a.upper())
    a = re.sub(r"\b(US|SD|SR|SH|CR|I|IH|RT|RTE)-(\w)", r"\1 \2", a)
    a = re.sub(r"\b(?:INTERSTATE(?: HIGHWAY| HWY)?|IH|I H)\s*(?=\d)", "I ", a)
    a = re.sub(r"\b(?:US|U S)\s+(?:HIGHWAY|HWY)\b", "US", a)
    a = re.sub(r"\b(?:FARM[- ]TO[- ]MARKET(?: ROAD| RD)?|FARM (?:ROAD|RD)|F M)\b", "FM", a)
    a = re.sub(r"\b(?:RANCH[- ]TO[- ]MARKET(?: ROAD| RD)?|RANCH (?:ROAD|RD)|RR|RM)\b(?=\s*\d)", "RM", a)
    a = re.sub(r"\b(?:STATE (?:HIGHWAY|HWY|ROAD|RD|ROUTE|RTE)|SR|SH|VERMONT (?:ROUTE|RTE|HIGHWAY|HWY)|SD (?:ROUTE|RTE|RT|HIGHWAY|HWY)|SD|"
               r"US (?:ROUTE|RTE|RT)|US|ROUTE|RTE|RT|HWY)\b\.?(?=\s*\d)", "SH", a)
    a = re.sub(r"\b(?:COUNTY (?:HIGHWAY|HWY|ROAD|RD)|CO RD|CTY (?:HWY|RD)|CR)\b", "CR", a)
    a = re.sub(r"\bHIGHWAY\b", "HWY", a)
    return re.sub(r"\b(US|SH|CR|HWY|FM|RM|I) (\w+)\s*-\s*\w+", r"\1 \2", a)


ORD = {"FIRST": "1ST", "SECOND": "2ND", "THIRD": "3RD", "FOURTH": "4TH", "FIFTH": "5TH", "SIXTH": "6TH", "SEVENTH": "7TH",
       "EIGHTH": "8TH", "NINTH": "9TH", "TENTH": "10TH", "ELEVENTH": "11TH", "TWELFTH": "12TH"}


def street_key(a):
    """'2505 Monroe St' -> ('2505', 'MONROE'); '1000 OSAGE STREET' -> ('1000', 'OSAGE'); 'E Colfax Ave' keeps 'COLFAX'."""
    if not isinstance(a, str):
        return None, None
    a = re.sub(r"[.,#]", " ", road(a))
    # "20940-A North Frederick Ave": a hyphenated unit letter is part of the number (Maryland's Montgomery County wrote them so)
    m = re.match(r"^\s*(\d+)(?:-?[A-Z])?(?:\s*-\s*\d+[A-Z]?)?\s+(.*)$", a)
    if not m:
        return None, None
    words = [w for w in m.group(2).split() if w]
    if len(words) > 1 and words[0] in DIRS:
        words = words[1:]
    core = []
    for w in words:
        if w in TYPES and core:
            break
        core.append(w)
    core = [ORD.get(w, w) for w in core]
    return m.group(1), " ".join(core[:3]) or None


def street_compat(a, b):
    """Same street, or one is a whole-word prefix of the other: Boulder's 2025 set sometimes truncates ("1206 CENTAUR" = Centaur Village Dr)."""
    if not isinstance(a, str) or not isinstance(b, str) or not a or not b:
        return False
    return a == b or a.startswith(b + " ") or b.startswith(a + " ")


def street_nums(a):
    """'157-159 W Main St' -> {'157', '159'}; '2505 Monroe St' -> {'2505'}."""
    if not isinstance(a, str):
        return set()
    a = road(a)
    m = re.match(r"^\s*(\d+)[A-Z]?(?:\s*-\s*(\d+)[A-Z]?)?\s", a.upper() + " ")
    if not m:
        return set()
    lo = int(m.group(1)); hi = int(m.group(2)) if m.group(2) else lo
    if hi < lo:   # "1500-02"
        hi = int(str(lo)[: len(str(lo)) - len(m.group(2))] + m.group(2)) if m.group(2) else lo
    return {str(x) for x in range(lo, hi + 1, 2 if (hi - lo) % 2 == 0 else 1)} if 0 <= hi - lo <= 12 else {str(lo)}


def _names(*vals):
    out = []
    for v in vals:
        if not isinstance(v, str):
            continue
        v = re.sub(r"\s*\((?:MOBILE|MOBILE UNIT|COMMISSARY|CATERING|SPECIAL EVENT|SPEC EVENT|TEMP(?:ORARY)? EVENT|CP|INSIDE [^)]*)\)\s*$", "", v, flags=re.I)
        for part in re.split(r"\s*/\s*|\s+\bdba\b\s+|\s+&\s+(?=[A-Z][a-z])", v, flags=re.I):
            k = norm_name(re.sub(r"\b(?:LLC|INC|CORP|CORPORATION|LTD|CO)\b\.?", "", part, flags=re.I))
            if k and k not in out:
                out.append(k)
    return out


META = json.load(open(os.path.join(OFF, "meta.json"))) if os.path.exists(os.path.join(OFF, "meta.json")) else {}
LIST_DATE = (META.get("siouxfalls") or {}).get("fetched")   # the day we read the City's layer
# the City's own page for inspection reports, and the state's search for everywhere else
MPLS_PAGE = "https://sweepsdata.siouxfalls.gov/Restaurants.aspx"
INSPECTIONS_URL = "https://sddoh.safefoodinspection.com/Inspection/publicinspectionsearch.aspx"
CODES = ["RB", "RW", "RL", "PL", "PD", "RR", "CL", "A-RL"]
ONPREM_T = tuple(f"Sioux Falls alcohol license, {lab} ({c})" for c in CODES for lab in ("on-sale", "on- and off-sale"))
MAKER_T = ()


def score_text(sc):
    """The City's score as shown: '96 of 100'."""
    return f"{int(sc)} of 100"


# every score 0..100 as text, in order: the app indexes results by position
RESULTS = tuple(score_text(x) for x in range(100, -1, -1))


def liq_kind(t):
    """A license type as shown -> on-premises or retail."""
    if not isinstance(t, str):
        return None
    return "onprem" if t in ONPREM_T else "retail" if "off-sale" in t else None


COLUMNS = ["jur", "lic", "name", "dba", "holder", "keys", "addr", "city", "zip", "num", "street", "lat", "lon", "kind", "active", "ltype",
           "insp", "issued", "biz", "drinks", "county"]


def _zip(z):
    z = re.sub(r"\D", "", str(z or ""))
    return z[:5] if len(z) >= 5 else ""


def _addr(a):
    """'2790 VETERANS MEMORIAL BLVD STE 130' -> '2790 Veterans Memorial Blvd Ste 130'; directions stay capitals ('N', 'SW')."""
    a = re.sub(r"\s+", " ", a or "").strip()
    a = re.sub(r"\b([A-Z]{2,})\b", lambda m: m.group(1).title(), a)
    a = re.sub(r"\b(\d+)(ST|ND|RD|TH)\b", lambda m: m.group(1) + m.group(2).lower(), a)   # "8TH" -> "8th"
    return re.sub(r"\b(Ne|Nw|Se|Sw)\b", lambda m: m.group(1).upper(), a)


def _city(c):
    return canon_city(" ".join(w.capitalize() for w in str(c or "").split())) if isinstance(c, str) and c.strip() else None


CT = ZoneInfo("America/Chicago")


def _ms(v):
    """An ArcGIS date (epoch milliseconds, UTC) -> YYYY-MM-DD in Sioux Falls' time (the City's own day)."""
    if not isinstance(v, (int, float)):
        return None
    return datetime.datetime.fromtimestamp(v / 1000, datetime.timezone.utc).astimezone(CT).date().isoformat()


# the City's site types that are a place to go out to eat; the rest (schools, hospitals, pools, casinos, groceries, convenience stores,
# hotels, caterers, clubs, stadiums, theatres) stay out. Mobile stands are trucks.
SF_FOOD = {"Restaurant", "Food Facility", "Fast Food Restaurant", "Bar", "Coffee Shop", "Restaurant & Bar", "Bakery", "Pizza Place",
           "Chinese Restaurant", "Mexican Restaurant", "Ice Cream Parlor"}
SF_TRUCK = {"Mobile Food Stand"}
_SITES = os.path.join(OFF, "siouxfalls", "restaurant_sites.json")
_DATES = [d for r in (json.load(open(_SITES)) if os.path.exists(_SITES) else []) for d in (_ms(r.get("INSP_DATE1")), _ms(r.get("INSP_DATE2"))) if d]
THROUGH = max(_DATES) if _DATES else None   # the latest inspection the City's layer holds


def load_sioux_falls():
    rows = []
    for r in json.load(open(_SITES)):
        name = re.sub(r"\s+", " ", r.get("SITE_NAME") or "").strip()
        name = re.sub(r"\s*\((?:MOBILE|SEASONAL)\)\s*$", "", name, flags=re.I)
        cat = (r.get("SITE_TYPE_DESC") or "").strip()
        kind = "food" if cat in SF_FOOD else "truck" if cat in SF_TRUCK else "other"
        addr = _addr(r.get("FULL_ADDRESS"))
        num, st = street_key(addr)
        visits = []
        for k_, (dk, sk) in enumerate((("INSP_DATE1", "SCORE1"), ("INSP_DATE2", "SCORE2"))):
            d, sc = _ms(r.get(dk)), r.get(sk)
            if d and isinstance(sc, (int, float)):
                visits.append([d, score_text(sc), "Inspection", f"{r.get('SITE_INV') or r.get('SITE_NO')}-{k_ + 1}"])
        visits.sort(key=lambda v: v[0], reverse=True)
        latest = max([v[0] for v in visits] + [d for d in (_ms(r.get("INSP_DATE1")),) if d], default=None)
        la, lo = r.get("LAT"), r.get("LON")
        rows.append({"jur": "siouxfalls", "lic": f"sf-{r.get('SITE_INV') or r.get('OBJECTID')}", "name": " ".join(w.capitalize() for w in name.split()) if name.isupper() else name,
                     "dba": name, "holder": None, "keys": _names(name), "addr": addr, "city": "Sioux Falls", "zip": "", "num": num, "street": st,
                     "lat": la if isinstance(la, (int, float)) else None, "lon": lo if isinstance(lo, (int, float)) else None,
                     "kind": kind, "active": bool(latest) and latest >= "2025-05-01",
                     "ltype": "Sioux Falls food service site (" + (cat or "unknown") + ")", "insp": visits, "issued": None,
                     "drinks": None, "county": None, "apn": None})
    return rows


def load_sf_liquor():
    rows = []
    for r in json.load(open(os.path.join(OFF, "siouxfalls", "alcohol_licenses.json"))):
        if (r.get("Status") or "").strip() != "Active":
            continue
        code = (r.get("LicenseType") or "").strip().upper()
        oo = re.sub(r"\s+", "", (r.get("On_OFF") or "").lower())
        lab = "on- and off-sale" if oo == "on/off" else "on-sale" if oo == "on" else "off-sale" if oo == "off" else None
        if not lab:
            continue
        name = re.sub(r"\s+", " ", r.get("BusinessName") or "").strip()
        addr = _addr(r.get("BusinessAddress"))
        num, st = street_key(addr)
        rows.append({"jur": "sf_liquor", "lic": f"sfliq-{r.get('OBJECTID')}", "name": name, "dba": name, "holder": None, "keys": _names(name),
                     "addr": addr, "city": "Sioux Falls", "zip": "", "num": num, "street": st, "lat": None, "lon": None,
                     "kind": "food" if lab != "off-sale" else "other", "active": True, "ltype": f"Sioux Falls alcohol license, {lab} ({code})",
                     "insp": [], "issued": None, "drinks": None, "county": None, "apn": None})
    return rows


def load():
    """Sioux Falls's food service sites (with the City's scores) and its alcohol licenses, joined by business."""
    rows = []
    if os.path.exists(_SITES):
        rows += load_sioux_falls()
    if os.path.exists(os.path.join(OFF, "siouxfalls", "alcohol_licenses.json")):
        rows += load_sf_liquor()
    df = pd.DataFrame(rows) if rows else pd.DataFrame({c: pd.Series(dtype=object) for c in COLUMNS + ["apn"]})
    for c_ in COLUMNS:
        if c_ not in df.columns:
            df[c_] = None
    df["lat"] = df["lat"].astype(float); df["lon"] = df["lon"].astype(float); df["active"] = df["active"].astype(bool)
    df["biz"] = np.arange(len(df))

    def join(a, b):
        old, new = df.at[b, "biz"], df.at[a, "biz"]
        if old != new:
            df.loc[df.biz == old, "biz"] = new
    # an alcohol license joins the active food site at its address (same house number and street) when the names agree or share a
    # distinctive word: one address can hold several businesses (a food hall, a hotel)
    food = df[(df.jur == "siouxfalls") & df.active & df.num.notna()]
    at = food.groupby("num").groups
    joined = 0
    for i in df.index[df.jur == "sf_liquor"]:
        cand = [j for j in at.get(df.at[i, "num"], []) if street_compat(df.at[i, "street"], df.at[j, "street"])]
        ki = df.at[i, "keys"] or []
        good = [j for j in cand if any(name_sim(p, q) >= 80 or ((_stems(p) - GENERIC) & (_stems(q) - GENERIC)) for p in ki for q in df.at[j, "keys"] or [])]
        if len({df.at[j, "biz"] for j in good}) == 1:
            join(good[0], i); joined += 1
    print("Sioux Falls alcohol licenses joined to a food site at their address:", joined, "of", int((df.jur == "sf_liquor").sum()))
    return df
