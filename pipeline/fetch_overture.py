"""Download the Overture Maps extracts that southdakota.py reads -> data/sd/

- overture_sd_bbox.parquet     every place in South Dakota's bounding box (name, category, address, point)
- overture_sd_sources.parquet  which datasets each South Dakota eating/drinking listing came from (Meta, Foursquare, ...)
- sd_shapes.json               simplified state and county outlines for the map
- sd_state_detail.geojson      the state outline at full detail, for the in-state test

Reads the public Overture bucket over S3 with DuckDB (no account needed). Ported from va-eats/pipeline/fetch_overture.py.
South Dakota: land division areas; the "counties" are its 66 (Oglala Lakota County is FIPS 46102, Shannon before 2015). The script
checks the border towns (North Sioux City and Sioux City, IA; Brandon; Lemmon on the North Dakota line; Spearfish and Belle Fourche near
Wyoming) so an Iowa, Nebraska, Minnesota, North Dakota, Montana or Wyoming listing stays out.
"""
import os, json, time
import duckdb
from shapely import wkb
from shapely.geometry import mapping, Polygon

RELEASE = "2026-10-21.0"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "sd")
# South Dakota (42.48°N–45.95°N, 96.44°W–104.06°W) plus a margin for the border towns
BBOX = "bbox.xmin BETWEEN -104.3 AND -96.3 AND bbox.ymin BETWEEN 42.3 AND 46.1"
EAT = "('restaurant','casual_eatery','bar','fast_food_restaurant','coffee_shop','cafe','smoothie_juice_bar','brewery','food_court')"
os.makedirs(OUT, exist_ok=True)

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial; SET s3_region='us-west-2';")
places = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=places/type=place/*.parquet"

t = time.time()
if not os.path.exists(f"{OUT}/overture_sd_bbox.parquet"):
    con.execute(f"""
COPY (
  SELECT id, names.primary AS name, basic_category AS cat, taxonomy.primary AS tax, taxonomy.hierarchy AS hier, confidence,
         operating_status AS status, brand.names.primary AS brand, addresses[1].freeform AS street, addresses[1].locality AS city,
         addresses[1].postcode AS zip, addresses[1].region AS region, ST_Y(geometry) AS lat, ST_X(geometry) AS lon, websites[1] AS web,
         phones[1] AS phone
  FROM read_parquet('{places}', hive_partitioning=1) WHERE {BBOX}
) TO '{OUT}/overture_sd_bbox.parquet' (FORMAT PARQUET)""")
    print("places in bbox", round(time.time() - t), "s", flush=True)
if not os.path.exists(f"{OUT}/overture_sd_sources.parquet"):
    con.execute(f"""
COPY (
  SELECT id, list_transform(sources, lambda x: x.dataset) AS ds, list_transform(sources, lambda x: x.update_time) AS ut,
         list_transform(sources, lambda x: x.record_id) AS rid,
         len(socials) AS n_soc, len(websites) AS n_web, len(phones) AS n_ph
  FROM read_parquet('{places}', hive_partitioning=1)
  WHERE {BBOX} AND basic_category IN {EAT}
) TO '{OUT}/overture_sd_sources.parquet' (FORMAT PARQUET)""")
    print("sources", round(time.time() - t), "s", flush=True)

areas = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=divisions/type=division_area/*.parquet"
rows = con.execute(f"""
  SELECT subtype, names.primary AS name, ST_AsWKB(geometry) AS g
  FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE country = 'US' AND region = 'US-SD' AND subtype IN ('region', 'county') AND class = 'land'
    AND bbox.xmin > -104.4 AND bbox.xmax < -96.2 AND bbox.ymin > 42.2 AND bbox.ymax < 46.2""").fetchall()


def rings(geom, tol, min_area):
    geom = geom.simplify(tol, preserve_topology=True)
    polys = [p for p in getattr(geom, "geoms", [geom]) if p.geom_type == "Polygon" and p.area >= min_area]
    return [[[round(x, 3), round(y, 3)] for x, y in p.exterior.coords] for p in polys]


out = {"state": None, "counties": []}
for sub, name, g in rows:
    geom = wkb.loads(bytes(g)).buffer(0)
    if sub == "region":
        json.dump(mapping(geom.simplify(0.0005, preserve_topology=True)), open(f"{OUT}/sd_state_detail.geojson", "w"))
        out["state"] = [[r] for r in rings(geom, 0.002, 0.000005)]
    else:
        out["counties"].append({"name": name, "c": rings(geom, 0.004, 0.00002)})
# full-detail county polygons for assigning each place to a county (not shipped)
json.dump({name: mapping(wkb.loads(bytes(g)).buffer(0).simplify(0.0003, preserve_topology=True))
           for sub, name, g in rows if sub == "county"}, open(f"{OUT}/sd_counties_detail.geojson", "w"))
json.dump(out, open(f"{OUT}/sd_shapes.json", "w"), separators=(",", ":"))
print("outlines: state", len(out["state"] or []), "rings +", len(out["counties"]), "counties;", round(time.time() - t), "s total")
# border towns: each must fall on the right side of the detailed state outline
from shapely.geometry import shape, Point
st = shape(json.load(open(f"{OUT}/sd_state_detail.geojson")))
for nm, lon, lat, want in [("Sioux Falls", -96.7311, 43.5446, True), ("North Sioux City", -96.4831, 42.5272, True), ("Brandon", -96.5717, 43.5947, True),
                           ("Lemmon", -102.1593, 45.9408, True), ("Spearfish", -103.8591, 44.4908, True), ("Belle Fourche", -103.8522, 44.6714, True),
                           ("Elk Point", -96.6837, 42.6833, True), ("Yankton", -97.3973, 42.8711, True), ("Rapid City", -103.2310, 44.0805, True),
                           ("Sioux City, IA", -96.4003, 42.4999, False), ("Akron, IA", -96.5592, 42.8286, False), ("Pipestone, MN", -96.3175, 43.9944, False),
                           ("Luverne, MN", -96.2128, 43.6544, False), ("Hankinson, ND", -96.9017, 46.0705, False), ("Sundance, WY", -104.3758, 44.4064, False),
                           ("Valentine, NE", -100.5510, 42.8728, False), ("South Sioux City, NE", -96.4136, 42.4739, False)]:
    ok = st.contains(Point(lon, lat))
    print(f"  {nm}: {'inside' if ok else 'outside'}{'' if ok == want else '  <-- WRONG'}")
print("counties:", len(out["counties"]), sorted(c["name"] for c in out["counties"]))

# the neighbours' land (North Dakota, South Dakota, Iowa, Wisconsin, Manitoba, Ontario): listings.py widens South Dakota's outline ~300 m
# for shores, but only where no neighbour's land is, so a Fargo, Superior or Hudson listing on the far side of the river stays out
nb = con.execute(f"""
  SELECT region, ST_AsWKB(geometry) FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE (country = 'US' AND region IN ('US-ND', 'US-MN', 'US-IA', 'US-NE', 'US-WY', 'US-MT'))
    AND subtype = 'region' AND class = 'land'""").fetchall()
from shapely.ops import unary_union
from shapely.geometry import box
near = box(-104.6, 42.0, -96.0, 46.4)
nbg = unary_union([wkb.loads(bytes(g)).buffer(0).intersection(near) for _, g in nb])
json.dump(mapping(nbg.simplify(0.0002, preserve_topology=True)), open(f"{OUT}/sd_neighbors.geojson", "w"))
print("neighbours:", sorted(r for r, _ in nb))
