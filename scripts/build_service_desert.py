#!/usr/bin/env python3
"""Build the Service Desert Score for all ~18,919 small areas (Plan 3).

Plan 1 gave per-SA *demand* (Vulnerability, by area). Plan 2 gave per-point
*supply* (care services, geocoded). Plan 3 fuses them by the only thing that
links a polygon to a point: distance.

  1. For each SA centroid, Haversine distance to the nearest supply point in
     each layer (home care, FCI, nursing homes).
  2. d_nearest = min over the COUNTED layers. Decision (handoff §4.1): only
     carer support counts — home care + FCI. Nursing homes are a residential
     *alternative*, not support for the informal carer, so they stay on the map
     but do not reduce the desert score. d_nursing is still stored for context.
  3. PR_distance = percentile rank of d_nearest (100 = furthest from any carer
     support). This completes the Isolation theme left open in Plan 1:
       Isolation     = mean(PR_nocar, PR_distance)
       Vulnerability = mean(Care load, Strain, Demand, Isolation)   ← recomputed
  4. Service Desert = Vulnerability x (PR_distance / 100).
     Multiplied, not averaged: an area scores high only with BOTH high need AND
     no carer support nearby. High need next door to a service scores low.

Honesty (handoff §3): supply points are geocoded to address / town / county.
The nearest point's precision flag is carried through (nl) so the UI can footnote
low-confidence distances. Office location is not service-delivery location — a
proxy for access, not a service boundary.

Inputs:
  data/sa_vulnerability.csv        per-SA themes + PR_nocar (Plan 1)
  site/sa/<region>.geojson         SA geometry (for centroids) + Plan 1 props
  data/homecare_agencies.geojson   COUNTED  (carer support)
  data/fci_centres.geojson         COUNTED  (carer support)
  data/nursing_homes.geojson       context only (residential alternative)

Outputs:
  data/sa_service_desert.csv       per-SA distances, PR_distance, updated
                                   isolation/vulnerability, service_desert
  site/sa/<region>.geojson         updated is/v props + new sd, dn, nt, nl
  site/sa/_meta.json               sd measure + recomputed is/v/sd breaks
  site/regions.json                recomputed is/v region means + sdMean
"""
import csv
import json
import math
from pathlib import Path

import numpy as np

from fetch_sa_boundaries import canon, slug
from build_vulnerability_index import (percentile_ranks, quantile_breaks, fnum,
                                        MEASURES as BASE_MEASURES)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE = ROOT / "site"
SA_OUT = SITE / "sa"

VULN_CSV = DATA / "sa_vulnerability.csv"

# layer key -> (geojson path, counts toward the desert distance?)
LAYERS = {
    "homecare": (DATA / "homecare_agencies.geojson", True),
    "fci":      (DATA / "fci_centres.geojson",       True),
    "nursing":  (DATA / "nursing_homes.geojson",     False),
}

EARTH_KM = 6371.0088


def avg(vals):
    v = [x for x in vals if x is not None]
    return round(sum(v) / len(v), 2) if v else None


def pct(vals, q):
    """Linear-interpolated q-quantile (q in 0..1) of non-null values."""
    s = sorted(x for x in vals if x is not None)
    if not s:
        return None
    i = q * (len(s) - 1)
    lo = int(i)
    hi = min(lo + 1, len(s) - 1)
    return round(s[lo] + (s[hi] - s[lo]) * (i - lo), 1)


# --------------------------------------------------------------------------
# load demand side (Plan 1) and SA geometry
# --------------------------------------------------------------------------
def load_vulnerability():
    """canon(SA code) -> {nocar (PR), cl, st, dm} from the Plan 1 CSV."""
    sa = {}
    for r in csv.DictReader(VULN_CSV.open()):
        sa[canon(r["sa_2022_code"])] = {
            "nocar": fnum(r["pr_nocar"]),
            "cl": fnum(r["care_load"]),
            "st": fnum(r["strain"]),
            "dm": fnum(r["demand"]),
        }
    return sa


def _ring_centroid(coords):
    """Area-weighted centroid of one polygon (list of [lon,lat] rings).
    Falls back to vertex mean for degenerate (zero-area) rings."""
    ring = coords[0]
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    a = cx = cy = 0.0
    for i in range(len(ring) - 1):
        cross = xs[i] * ys[i + 1] - xs[i + 1] * ys[i]
        a += cross
        cx += (xs[i] + xs[i + 1]) * cross
        cy += (ys[i] + ys[i + 1]) * cross
    if a == 0:
        return sum(xs) / len(xs), sum(ys) / len(ys)
    a *= 0.5
    return cx / (6 * a), cy / (6 * a)


def feature_centroid(geom):
    """(lon, lat) centroid for Polygon / MultiPolygon. For MultiPolygon, take
    the largest part's centroid (by vertex count — a cheap, robust proxy)."""
    if geom["type"] == "Polygon":
        return _ring_centroid(geom["coordinates"])
    parts = geom["coordinates"]
    biggest = max(parts, key=lambda poly: len(poly[0]))
    return _ring_centroid(biggest)


def load_sa_geometry():
    """Read every region geojson once. Returns the loaded FeatureCollections
    (for write-back) and a flat list of (region, idx, canon_code, lon, lat)."""
    meta = json.loads((SA_OUT / "_meta.json").read_text())
    fcs, records = {}, []
    for region, info in meta["regions"].items():
        fc = json.loads((SITE / info["file"]).read_text())
        fcs[region] = fc
        for idx, ft in enumerate(fc["features"]):
            lon, lat = feature_centroid(ft["geometry"])
            records.append((region, idx, canon(ft["properties"]["c"]), lon, lat))
    return meta, fcs, records


# --------------------------------------------------------------------------
# supply side (Plan 2)
# --------------------------------------------------------------------------
def load_layer(path):
    """Return (lat[], lon[], loc[]) numpy arrays for a supply geojson, or None
    if the file is absent (geocoding still running)."""
    if not path.exists():
        return None
    fc = json.loads(path.read_text())
    lats, lons, locs = [], [], []
    for ft in fc["features"]:
        lon, lat = ft["geometry"]["coordinates"]
        lats.append(lat)
        lons.append(lon)
        locs.append(ft["properties"].get("loc", "address"))
    return np.array(lats), np.array(lons), locs


def nearest_distance(sa_lat, sa_lon, layer):
    """Vectorised Haversine. For SA centroids (N,) vs a layer's points (M,),
    return (min_dist_km[N], argmin_idx[N]). Ireland is small — one N x M matrix."""
    plat, plon, _ = layer
    rlat = np.radians(sa_lat)[:, None]
    rlon = np.radians(sa_lon)[:, None]
    plat_r = np.radians(plat)[None, :]
    plon_r = np.radians(plon)[None, :]
    dlat = plat_r - rlat
    dlon = plon_r - rlon
    a = np.sin(dlat / 2) ** 2 + np.cos(rlat) * np.cos(plat_r) * np.sin(dlon / 2) ** 2
    d = 2 * EARTH_KM * np.arcsin(np.sqrt(a))
    return d.min(axis=1), d.argmin(axis=1)


DENSITY_KM = 25.0   # "services within N km" — a supply-choice measure alongside nearest.
#                     25 km ≈ a realistic carer-support catchment (home-care travel range;
#                     FCI centres serve whole counties). Stored in _meta so the UI labels it.


def count_within(sa_lat, sa_lon, layers_list, radius_km):
    """Count supply points within radius_km of each SA centroid, over the combined
    points of the given layers. Complements nearest-distance: a lone office can be
    close (low d_nearest) yet be the ONLY one (count 1), vs a town with many. Returns
    an int array (N,)."""
    plat = np.concatenate([l[0] for l in layers_list])
    plon = np.concatenate([l[1] for l in layers_list])
    rlat = np.radians(sa_lat)[:, None]
    rlon = np.radians(sa_lon)[:, None]
    pa = np.radians(plat)[None, :]
    po = np.radians(plon)[None, :]
    dlat = pa - rlat
    dlon = po - rlon
    a = np.sin(dlat / 2) ** 2 + np.cos(rlat) * np.cos(pa) * np.sin(dlon / 2) ** 2
    d = 2 * EARTH_KM * np.arcsin(np.sqrt(a))
    return (d <= radius_km).sum(axis=1)


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
def build():
    vuln = load_vulnerability()
    meta, fcs, records = load_sa_geometry()
    print(f"  loaded {len(records)} SA centroids, {len(vuln)} vulnerability rows")

    layers, missing = {}, []
    for key, (path, _counts) in LAYERS.items():
        layer = load_layer(path)
        if layer is None:
            missing.append(path.name)
        else:
            layers[key] = layer
            print(f"  {key:9s} {len(layer[0]):4d} points  ({path.name})")

    counted = [k for k, (_p, c) in LAYERS.items() if c]
    if any(k not in layers for k in counted):
        still = ", ".join(missing)
        raise SystemExit(
            f"\nCOUNTED supply layer(s) not yet written: {still}.\n"
            f"fetch_supply.py is still geocoding — re-run this script once it "
            f"finishes (the three data/*.geojson exist).")

    sa_lat = np.array([r[4] for r in records])  # note: feature_centroid -> (lon,lat)
    sa_lon = np.array([r[3] for r in records])

    # distance to nearest point in each available layer
    dist = {}
    nearest_idx = {}
    for key, layer in layers.items():
        d, idx = nearest_distance(sa_lat, sa_lon, layer)
        dist[key] = d
        nearest_idx[key] = idx

    # d_nearest over COUNTED layers only; track which type/precision won
    counted_present = [k for k in counted if k in layers]
    stacked = np.vstack([dist[k] for k in counted_present])          # (L, N)
    d_nearest = stacked.min(axis=0)
    which = stacked.argmin(axis=0)                                   # row -> layer
    nearest_type = [counted_present[w] for w in which]
    nearest_loc = [layers[counted_present[w]][2][nearest_idx[counted_present[w]][i]]
                   for i, w in enumerate(which)]

    # carer-support services within 10 km (combined home care + FCI) — a supply-choice
    # measure alongside nearest distance; 0 = no carer support within 10 km at all
    n_within = count_within(sa_lat, sa_lon, [layers[k] for k in counted_present], DENSITY_KM)

    # PR_distance: higher distance -> higher rank (100 = furthest from support)
    pr_dist = percentile_ranks([(i, float(d)) for i, d in enumerate(d_nearest)])

    # recompute isolation + vulnerability, then the service desert score
    rows = []
    for i, (region, idx, code, lon, lat) in enumerate(records):
        v = vuln.get(code, {})
        prd = pr_dist.get(i)
        iso = avg([v.get("nocar"), prd])
        vul = avg([v.get("cl"), v.get("st"), v.get("dm"), iso])
        sd = round(vul * prd / 100, 2) if (vul is not None and prd is not None) else None
        rec = {
            "code": code, "region": region, "idx": idx, "lon": lon, "lat": lat,
            "d_nursing": round(float(dist["nursing"][i]), 2) if "nursing" in dist else None,
            "d_homecare": round(float(dist["homecare"][i]), 2),
            "d_fci": round(float(dist["fci"][i]), 2),
            "d_nearest": round(float(d_nearest[i]), 2),
            "nsup": int(n_within[i]),
            "nt": nearest_type[i], "nl": nearest_loc[i],
            "prd": prd, "is": iso, "v": vul, "sd": sd,
        }
        rows.append(rec)
    return meta, fcs, rows


# --------------------------------------------------------------------------
# outputs
# --------------------------------------------------------------------------
def write_csv(rows):
    cols = ["sa_2022_code", "d_nursing_km", "d_homecare_km", "d_fci_km",
            "d_nearest_km", "support_nearby", "nearest_type", "nearest_loc",
            "pr_distance", "isolation", "vulnerability", "service_desert"]
    with (DATA / "sa_service_desert.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in sorted(rows, key=lambda x: x["code"]):
            w.writerow([r["code"], r["d_nursing"], r["d_homecare"], r["d_fci"],
                        r["d_nearest"], r["nsup"], r["nt"], r["nl"], r["prd"],
                        r["is"], r["v"], r["sd"]])
    print(f"  wrote data/sa_service_desert.csv ({len(rows)} small areas)")


def update_geojson(fcs, rows):
    """Write the new is/v values and add sd, dn (nearest km), nt, nl per feature."""
    by_region = {}
    for r in rows:
        by_region.setdefault(r["region"], {})[r["idx"]] = r
    for region, fc in fcs.items():
        rmap = by_region.get(region, {})
        for idx, ft in enumerate(fc["features"]):
            r = rmap.get(idx)
            if not r:
                continue
            p = ft["properties"]
            p["is"] = r["is"]
            p["v"] = r["v"]
            p["sd"] = r["sd"]
            p["prd"] = round(r["prd"], 1) if r["prd"] is not None else None  # distance rank (bivariate X)
            p["dn"] = round(r["d_nearest"], 1)
            p["nsup"] = r["nsup"]
            p["nt"] = r["nt"]
            p["nl"] = r["nl"]
        path = SA_OUT / f"{slug(region)}.geojson"
        path.write_text(json.dumps(fc, separators=(",", ":")))
    print(f"  updated {len(fcs)} region geojson files")


def update_meta(meta, rows):
    measures = dict(BASE_MEASURES)            # v, cl, st, dm, is
    measures["sd"] = "Support gap"
    meta["measures"] = measures
    meta["density_km"] = DENSITY_KM   # radius for the "services within N km" tooltip
    allv = {"is": [r["is"] for r in rows],
            "v": [r["v"] for r in rows],
            "sd": [r["sd"] for r in rows]}
    for m in ("is", "v", "sd"):
        meta["breaks"][m] = quantile_breaks(allv[m])
    # national 1/3 and 2/3 quantiles per axis, for the Need x Supply bivariate splits
    # (the visuals load SA files per-region, so they can't compute national terciles)
    vv = [r["v"] for r in rows]
    pp = [r["prd"] for r in rows]
    meta["terciles"] = {"v": [pct(vv, 1 / 3), pct(vv, 2 / 3)],
                        "prd": [pct(pp, 1 / 3), pct(pp, 2 / 3)]}
    meta["note"] = ("Percentile rank across 18,919 small areas (0-100, 100 = "
                    "greatest need). Service desert = Vulnerability x distance to "
                    "nearest carer support (home care / FCI); high only where need "
                    "and isolation coincide.")
    (SA_OUT / "_meta.json").write_text(json.dumps(meta, indent=1))
    print("  updated site/sa/_meta.json (sd measure + is/v/sd breaks)")


def patch_regions(rows):
    p90 = pct([r["v"] for r in rows], 0.9)   # national top-decile vulnerability threshold
    acc = {}
    for r in rows:
        a = acc.setdefault(r["region"], {"is": [0.0, 0], "v": [0.0, 0], "sd": [0.0, 0],
                                         "prd": [0.0, 0], "vlist": [], "top": 0})
        for m in ("is", "v", "sd", "prd"):
            if r[m] is not None:
                a[m][0] += r[m]
                a[m][1] += 1
        if r["v"] is not None:
            a["vlist"].append(r["v"])
            if p90 is not None and r["v"] >= p90:
                a["top"] += 1
    path = SITE / "regions.json"
    regions = json.loads(path.read_text())
    for d in regions:
        a = acc.get(d["region"])
        if not a:
            continue
        for m in ("is", "v", "sd", "prd"):
            d[f"{m}Mean"] = round(a[m][0] / a[m][1], 2) if a[m][1] else None
        # spread bar + hidden-hotspot badge (internal SA distribution within the region)
        d["vP05"] = pct(a["vlist"], 0.05)
        d["vP95"] = pct(a["vlist"], 0.95)
        d["vTop10"] = a["top"]            # count of this region's SAs in the national top decile
    path.write_text(json.dumps(regions, indent=1))
    print(f"  patched site/regions.json (is/v/sd/prd means + vP05/vP95/vTop10; "
          f"national v P90={p90})")


def write_top(rows, n=100):
    """The top-N SAs by Service Desert Score, with centroids so the map can drop
    markers (they span regions and aren't all loaded at once) and a table can
    list the greatest unmet need. Drives the Plan 3 highlight toggle + table.
    Carries the nearest-settlement name so the table reads as places, not codes."""
    towns = {}
    town_csv = ROOT / "data" / "sa_town_names.csv"
    if town_csv.exists():
        with town_csv.open() as f:
            towns = {r["sa_2022_code"]: r for r in csv.DictReader(f)}
    ranked = sorted((r for r in rows if r["sd"] is not None),
                    key=lambda r: -r["sd"])[:n]
    out = []
    for r in ranked:
        t = towns.get(r["code"]) or towns.get(r["code"].split("/")[0]) or {}
        out.append({"c": r["code"], "region": r["region"], "sd": r["sd"], "v": r["v"],
                    "dn": round(r["d_nearest"], 1), "nt": r["nt"], "nl": r["nl"],
                    "town": t.get("town_name", ""), "county": t.get("county", ""),
                    "lon": round(r["lon"], 5), "lat": round(r["lat"], 5)})
    (SA_OUT / "top_desert.json").write_text(json.dumps(out, separators=(",", ":")))
    print(f"  wrote site/sa/top_desert.json (top {len(out)})")


def report(rows):
    ranked = sorted((r for r in rows if r["sd"] is not None),
                    key=lambda r: -r["sd"])[:10]
    print("\nTop 10 small areas by Service Desert Score:")
    for r in ranked:
        flag = "" if r["nl"] == "address" else f"  [~{r['nl']}]"
        print(f"  {r['code']:20s} sd={r['sd']:5.1f}  v={r['v']:5.1f}  "
              f"{r['d_nearest']:5.1f} km to {r['nt']}{flag}")
    coarse = sum(1 for r in rows if r["nl"] != "address")
    print(f"\n{coarse}/{len(rows)} SAs have a town/county-geocoded nearest point "
          f"(distance is a lower-confidence estimate for those).")
    none20 = sum(1 for r in rows if r["nsup"] == 0)
    one20 = sum(1 for r in rows if r["nsup"] == 1)
    print(f"Supply within {DENSITY_KM:.0f} km: {none20} SAs have NONE, {one20} have only one "
          f"carer-support service nearby (a lone-office desert the nearest-distance alone misses).")


def main():
    meta, fcs, rows = build()
    write_csv(rows)
    update_geojson(fcs, rows)
    update_meta(meta, rows)
    patch_regions(rows)
    write_top(rows)
    report(rows)


if __name__ == "__main__":
    main()
