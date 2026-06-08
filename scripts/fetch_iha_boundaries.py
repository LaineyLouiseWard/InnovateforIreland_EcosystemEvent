#!/usr/bin/env python3
"""Fetch HSE Integrated Healthcare Area (IHA) boundaries — the 20 home-support
service areas across 6 health regions, the geography for Plan 4 (Market Gap).

Source : ArcGIS "HSE Integrated Healthcare Areas (2025) generalised (20m)"
         GeoHive / Tailte Eireann, CC-BY-4.0, keyless. Built from CSO Small
         Areas 2022, so SAs nest cleanly within IHAs.
         https://www.geohive.ie/datasets/7c0665223cda494aa22b5dee643a0ac0_0
         Accessed 2026-06-08.
Output : data/boundaries/iha_2025.geojson  (20 polygons, WGS84, coords rounded)
         Join keys carried: IHA_code, IHA_operational_name, HR_code,
         HR_operational_name.

Note   : the SA boundary layer carries NO IHA field, so the SA->IHA crosswalk
         needed by Plan 4 must come from a spatial join (SA centroid in IHA
         polygon), not an attribute lookup. This script only fetches geometry.
"""
import json, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT / "data" / "boundaries" / "iha_2025.geojson"
BASE = ("https://services-eu1.arcgis.com/BuS9rtTsYEV5C0xh/arcgis/rest/services/"
        "HealthGeographies_2025_IHA_generalised_20m/FeatureServer/0/query")
FIELDS = "IHA_code,IHA_operational_name,HR_code,HR_operational_name"


def round_coords(obj, nd=5):
    if isinstance(obj, (int, float)):
        return round(obj, nd)
    return [round_coords(x, nd) for x in obj]


def main():
    q = urllib.parse.urlencode({"where": "1=1", "outFields": FIELDS,
                                "outSR": 4326, "f": "geojson"})
    print("Fetching HSE IHA boundaries ...")
    with urllib.request.urlopen(f"{BASE}?{q}", timeout=180) as r:
        fc = json.load(r)

    feats = [{"type": "Feature",
              "geometry": {"type": ft["geometry"]["type"],
                           "coordinates": round_coords(ft["geometry"]["coordinates"])},
              "properties": ft["properties"]}
             for ft in fc["features"]]
    feats.sort(key=lambda f: f["properties"]["IHA_code"])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"type": "FeatureCollection", "features": feats},
                              separators=(",", ":")))
    print(f"  {len(feats)} IHAs  ->  {OUT.relative_to(ROOT)}  ({OUT.stat().st_size/1024:.0f} KB)")
    for f in feats:
        p = f["properties"]
        print(f"    {p['IHA_code']:>3}  {p['IHA_operational_name']:<45} [{p['HR_operational_name']}]")


if __name__ == "__main__":
    main()
