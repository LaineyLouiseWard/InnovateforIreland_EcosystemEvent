#!/usr/bin/env python3
"""Bake the Now base-layer data for the carer at-risk map into the static site/.

Reads the processed carer-rate table and the NUTS3 boundary, joins them by region
name, and writes the two files the Leaflet page loads (no fetch/CORS in the browser):

  site/regions.json     one row per region: carers2022, population2022, carerRate, rankNow
  site/regions.geojson  the 8 region polygons, each with properties.region

The State/"Ireland" (IE0) total row is dropped — the map shows the 8 regions only.
Region names are the join key; the CSO carer table and the GeoHive boundary both use
"Midlands" (plural), so the join is clean — this script aborts loudly if it isn't.

Source CSV : data/carer_rate_nuts3.csv      (scripts/fetch_carer_data.py, CSO Census 2022)
Boundary   : data/boundaries/nuts3_2016.geojson  (GeoHive / Tailte Éireann, NUTS3NAME)
Stdlib only, repo-relative paths — runnable on any machine with Python 3.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_IN = ROOT / "data" / "carer_rate_nuts3.csv"
GEO_IN = ROOT / "data" / "boundaries" / "nuts3_2016.geojson"
SITE = ROOT / "site"
JSON_OUT = SITE / "regions.json"
GEO_OUT = SITE / "regions.geojson"

STATE_ROW = "Ireland"      # the IE0 national total — mapped as context, not a region
COORD_DECIMALS = 4         # ~11 m: ample for an 8-region national choropleth, ~halves file size


def load_regions():
    """Read the carer-rate CSV, drop the State total, rank by carer rate (1 = highest)."""
    rows = []
    with CSV_IN.open() as f:
        for r in csv.DictReader(f):
            if r["region"] == STATE_ROW:
                continue
            rows.append({
                "region": r["region"],
                "carers2022": int(float(r["carers"])),
                "population2022": int(float(r["population"])),
                "carerRate": round(float(r["carer_rate_pct"]), 3),
            })
    rows.sort(key=lambda d: d["carerRate"], reverse=True)
    for i, d in enumerate(rows, start=1):
        d["rankNow"] = i
    return rows


def round_ring(ring):
    """Round a ring's coordinates, drop points that collapse onto their neighbour, and
    keep it closed. Returns None if it degenerates below a valid linear ring (4 points)
    — tiny offshore rocks that round away to a line, not meaningful at national scale."""
    pts = [[round(x, COORD_DECIMALS), round(y, COORD_DECIMALS)] for x, y in ring]
    out = [pts[0]]
    for p in pts[1:]:
        if p != out[-1]:
            out.append(p)
    if out[0] != out[-1]:
        out.append(out[0])
    return out if len(out) >= 4 else None


def clean_polygon(rings):
    """Round each ring; drop collapsed holes, drop the whole part if its outer ring
    collapses. Returns the cleaned ring list, or None if the part is gone."""
    cleaned = []
    for i, ring in enumerate(rings):
        r = round_ring(ring)
        if r is not None:
            cleaned.append(r)
        elif i == 0:
            return None      # outer ring collapsed → this polygon part disappears
    return cleaned or None


def clean_geometry(geom):
    """Round + simplify a Polygon / MultiPolygon, dropping degenerate rings/parts."""
    if geom["type"] == "Polygon":
        poly = clean_polygon(geom["coordinates"])
        return {"type": "Polygon", "coordinates": poly} if poly else None
    if geom["type"] == "MultiPolygon":
        parts = [p for p in (clean_polygon(r) for r in geom["coordinates"]) if p]
        return {"type": "MultiPolygon", "coordinates": parts} if parts else None
    return geom


def build_geojson(region_names):
    """Rewrite the boundary so each feature carries properties.region (the join key),
    rounding coordinates to keep the served file light. Verifies the 8-way join."""
    geo = json.loads(GEO_IN.read_text())
    feats, geo_names = [], []
    for ft in geo["features"]:
        name = ft["properties"]["NUTS3NAME"]
        geo_names.append(name)
        geom = clean_geometry(ft["geometry"])
        if geom is None:
            raise SystemExit(f"Region {name!r} lost all geometry after simplification.")
        feats.append({
            "type": "Feature",
            "properties": {"region": name, "nuts3": ft["properties"]["NUTS3"]},
            "geometry": geom,
        })
    # The silent-failure guard: every data region must have a polygon and vice versa.
    missing = sorted(set(region_names) - set(geo_names))
    extra = sorted(set(geo_names) - set(region_names))
    if missing or extra:
        raise SystemExit(
            f"Region-name join FAILED.\n  in CSV, no polygon: {missing}\n  polygon, not in CSV: {extra}"
        )
    return {"type": "FeatureCollection", "features": feats}, geo_names


def main():
    SITE.mkdir(exist_ok=True)
    regions = load_regions()
    region_names = [d["region"] for d in regions]
    geojson, geo_names = build_geojson(region_names)

    JSON_OUT.write_text(json.dumps(regions, indent=1))
    GEO_OUT.write_text(json.dumps(geojson))

    # Report — the validate step from the build brief.
    pop = sum(d["population2022"] for d in regions)
    carers = sum(d["carers2022"] for d in regions)
    print(f"Wrote {JSON_OUT.relative_to(ROOT)} ({len(regions)} regions) "
          f"and {GEO_OUT.relative_to(ROOT)} ({len(geojson['features'])} features)")
    print(f"Join: all {len(region_names)} regions matched a polygon "
          f"({', '.join(sorted(region_names))})")
    print(f"National carer rate (regions summed): {100 * carers / pop:.2f}%  "
          f"({carers:,} carers / {pop:,} people)")
    print("Rank (1 = highest carer rate):")
    for d in regions:
        print(f"  {d['rankNow']}. {d['region']:<11} {d['carerRate']:.2f}%  "
              f"({d['carers2022']:,} carers)")


if __name__ == "__main__":
    main()
