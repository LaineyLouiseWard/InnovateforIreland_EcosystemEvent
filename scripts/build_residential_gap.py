#!/usr/bin/env python3
"""Residential-care gap: where care demand is high but the nearest nursing home is far.

The nursing-home analogue of the Service Desert. The Service Desert serves *in-home*
carer support (home care / FCI); this serves *residential* operators (nursing homes).

  rd = Demand x (PR_nursing_distance / 100)
       Demand = PR(disability rate + over-65 share)  -- who is likely to need care
       PR_nursing_distance = percentile rank of distance to the nearest nursing home
                             (100 = furthest). Multiplied, not averaged: high only
                             where care demand AND distance-to-a-home both run high.

This is an ADDITIVE patch over the deployed site/ data. It recomputes nothing that
build_service_desert.py already produced (v, sd, dm ...); it only adds the new `rd`
measure, so re-running it cannot shift the existing scores.

Inputs (deployed site/ data only, no data/ dependency):
  site/sa/<region>.geojson          SA geometry + existing `dm` (Demand PR)
  site/supply/nursing_homes.geojson the residential layer
Outputs (in place, additive):
  site/sa/<region>.geojson          + rd, dnn (km to nearest home), prn (distance PR)
  site/sa/_meta.json                + "rd" in measures + breaks
  site/regions.json                 + rdMean per region
"""
import json
from pathlib import Path

import numpy as np

from build_service_desert import feature_centroid, nearest_distance, load_layer
from build_vulnerability_index import percentile_ranks, quantile_breaks

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SA = SITE / "sa"
NURSING = SITE / "supply" / "nursing_homes.geojson"


def main():
    meta = json.loads((SA / "_meta.json").read_text())
    nursing = load_layer(NURSING)
    if nursing is None:
        raise SystemExit(f"missing {NURSING}")

    fcs, files, records, lats, lons = {}, {}, [], [], []
    for region, info in meta["regions"].items():
        fc = json.loads((SITE / info["file"]).read_text())
        fcs[region] = fc
        files[region] = info["file"]
        for idx, ft in enumerate(fc["features"]):
            lon, lat = feature_centroid(ft["geometry"])
            lats.append(lat)
            lons.append(lon)
            records.append((region, idx, ft["properties"].get("dm")))
    print(f"  {len(records)} SA centroids, {len(nursing[0])} nursing homes")

    d_nursing, _ = nearest_distance(np.array(lats), np.array(lons), nursing)
    pr_n = percentile_ranks([(i, float(d)) for i, d in enumerate(d_nursing)])

    all_rd = []
    for i, (region, idx, dm) in enumerate(records):
        prn = pr_n.get(i)
        rd = round(dm * prn / 100, 2) if (dm is not None and prn is not None) else None
        p = fcs[region]["features"][idx]["properties"]
        p["rd"] = rd
        p["dnn"] = round(float(d_nursing[i]), 1)
        p["prn"] = round(prn, 1) if prn is not None else None
        all_rd.append((region, rd))

    for region, fc in fcs.items():
        (SITE / files[region]).write_text(json.dumps(fc, separators=(",", ":")))

    meta.setdefault("measures", {})["rd"] = "Nursing-home gap"
    meta["breaks"]["rd"] = quantile_breaks([rd for _, rd in all_rd if rd is not None])
    (SA / "_meta.json").write_text(json.dumps(meta, indent=1))

    acc = {}
    for region, rd in all_rd:
        if rd is None:
            continue
        a = acc.setdefault(region, [0.0, 0])
        a[0] += rd
        a[1] += 1
    regions = json.loads((SITE / "regions.json").read_text())
    for d in regions:
        a = acc.get(d["region"])
        d["rdMean"] = round(a[0] / a[1], 2) if a and a[1] else None
    (SITE / "regions.json").write_text(json.dumps(regions, indent=1))

    scored = sum(1 for _, rd in all_rd if rd is not None)
    print(f"  added rd to {len(fcs)} region files; {scored} SAs scored")
    top = sorted([(r, rd) for r, rd in all_rd if rd is not None], key=lambda x: -x[1])[:5]
    print("  highest residential gap (region, rd):", top)


if __name__ == "__main__":
    main()
