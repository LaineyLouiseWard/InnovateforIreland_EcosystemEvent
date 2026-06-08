#!/usr/bin/env python3
"""Fetch CSO Small Area 2022 boundaries, join the carer data, and bake one
GeoJSON per NUTS3 region for the zoom-in map.

Source : ArcGIS SMALL_AREA_2022_Generalised_20m (Tailte Eireann / CSO), keyless.
Join   : SA_PUB2022 <-> data/carer_at_risk_small_area.csv sa_2022_code, matched on
         a canonical form (each numeric part zero-padded to 9 digits) — verified 1:1
         over all 18,919 areas.
Outputs: site/sa/<region-slug>.geojson  (carer rate + isolation baked into props)
         site/sa/_meta.json             (quantile colour breaks per measure)
Raw cache (gitignored): data/raw/sa_2022_boundaries.geojson
"""
import csv, json, re, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW  = ROOT / "data" / "raw" / "sa_2022_boundaries.geojson"
OUT  = ROOT / "site" / "sa"
DATA = ROOT / "data" / "carer_at_risk_small_area.csv"
BASE = ("https://services-eu1.arcgis.com/BuS9rtTsYEV5C0xh/ArcGIS/rest/services/"
        "SMALL_AREA_2022_Genralised_20m_view/FeatureServer/0/query")
PAGE = 2000


def canon(code):
    return "/".join(p.zfill(9) if (p.isdigit() and len(p) >= 8) else p
                    for p in code.split("/"))


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def fetch_all():
    if RAW.exists():
        print(f"  using cached {RAW.relative_to(ROOT)}")
        return json.loads(RAW.read_text())
    feats, off = [], 0
    while True:
        q = urllib.parse.urlencode({"where": "1=1",
            "outFields": "SA_PUB2022,SA_NUTS3_NAME", "outSR": 4326,
            "resultOffset": off, "resultRecordCount": PAGE, "f": "geojson"})
        with urllib.request.urlopen(f"{BASE}?{q}", timeout=180) as r:
            d = json.load(r)
        page = d.get("features", [])
        feats.extend(page)
        print(f"  fetched {len(feats)} / 18919")
        if len(page) < PAGE:
            break
        off += PAGE
    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(json.dumps({"type": "FeatureCollection", "features": feats}))
    return {"type": "FeatureCollection", "features": feats}


def load_data():
    out = {}
    for row in csv.DictReader(open(DATA)):
        def f(k):
            v = row.get(k, "")
            try: return round(float(v), 2)
            except (TypeError, ValueError): return None
        out[canon(row["sa_2022_code"])] = {
            "r": f("carer_rate_pct"), "o": f("one_person_hh_pct"), "n": f("no_car_hh_pct")}
    return out


def round_coords(obj, nd=5):
    if isinstance(obj, (int, float)):
        return round(obj, nd)
    return [round_coords(x, nd) for x in obj]


def quantile_breaks(values, n=6):
    vs = sorted(v for v in values if v is not None)
    if not vs:
        return []
    # interior breaks between n equal-count classes
    return [round(vs[int(len(vs) * i / n)], 2) for i in range(1, n)]


def main():
    print("Fetching small-area boundaries ...")
    fc = fetch_all()
    data = load_data()
    OUT.mkdir(parents=True, exist_ok=True)

    by_region, missing = {}, 0
    for ft in fc["features"]:
        p = ft.get("properties", {})
        key = canon(p["SA_PUB2022"])
        rec = data.get(key)
        if rec is None:
            missing += 1
            continue
        region = p["SA_NUTS3_NAME"]
        feat = {"type": "Feature",
                "geometry": {"type": ft["geometry"]["type"],
                             "coordinates": round_coords(ft["geometry"]["coordinates"])},
                "properties": {"c": p["SA_PUB2022"], **rec}}
        by_region.setdefault(region, []).append(feat)

    index = {}
    for region, feats in sorted(by_region.items()):
        path = OUT / f"{slug(region)}.geojson"
        path.write_text(json.dumps({"type": "FeatureCollection", "features": feats},
                                   separators=(",", ":")))
        index[region] = {"file": f"sa/{slug(region)}.geojson", "count": len(feats),
                         "kb": round(path.stat().st_size / 1024)}
        print(f"  {region:12s} {len(feats):5d} areas  {index[region]['kb']:5d} KB")

    allvals = {m: [r[m] for r in data.values()] for m in ("r", "o", "n")}
    meta = {"regions": index, "missing_join": missing,
            "breaks": {m: quantile_breaks(allvals[m]) for m in allvals},
            "measures": {"r": "Carer rate (%)", "n": "No-car households (%)",
                         "o": "One-person households (%)"}}
    (OUT / "_meta.json").write_text(json.dumps(meta, indent=1))
    print(f"\nDone. unmatched polygons: {missing}.  meta breaks: {meta['breaks']}")


if __name__ == "__main__":
    main()
