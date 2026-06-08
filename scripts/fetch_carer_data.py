#!/usr/bin/env python3
"""Fetch Census 2022 carer and population data from the CSO PxStat API and
compute carer rates for the carer-at-risk map (the base layer).

Source: CSO PxStat JSON-stat API — keyless, open, no login.
  https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/<CODE>/JSON-stat/2.0/en
Accessed: 2026-06-08

Tables (see docs/DATA.md):
  SAP2022T12T2NUTS  carers by NUTS3 region        SAP2022T1T1NUTS  population by NUTS3
  SAP2022T12T2SA    carers by small area          SAP2022T1T1SA    population by small area

Outputs:
  data/raw/<CODE>.json             raw pulls (gitignored, re-pulled by this script)
  data/carer_rate_nuts3.csv        8 NUTS3 regions + State — the build-first base map
  data/carer_rate_small_area.csv   ~18,920 small areas — the zoom-in layer
"""
import csv
import json
import urllib.request
from pathlib import Path

API = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/{code}/JSON-stat/2.0/en"
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data"

# Dimension ids are stable across these tables
NUTS3 = "C03880V04631"
SA = "C04172V04943"
SEX = "C03738V04487"
AGE = "C03737V04485"
HH = "C03774V04528"   # household composition (SAP2022T5T1SA)
CAR = "C03768V04517"  # number of cars (SAP2022T15T1SA)
CAR_BANDS = ["No motor car", "1 motor car", "2 motor cars", "3 motor cars",
             "4 or more motor cars"]


def fetch(code):
    RAW.mkdir(parents=True, exist_ok=True)
    dest = RAW / f"{code}.json"
    if not dest.exists():
        print(f"  fetching {code} ...")
        with urllib.request.urlopen(API.format(code=code), timeout=120) as r:
            dest.write_bytes(r.read())
    return json.loads(dest.read_text())


def _pos_of(dim, label):
    """Position of the category whose label == label."""
    code = next(c for c, lbl in dim["category"]["label"].items() if lbl == label)
    idx = dim["category"]["index"]
    return idx[code] if isinstance(idx, dict) else list(idx).index(code)


def _strides(size):
    s = [1] * len(size)
    for i in range(len(size) - 2, -1, -1):
        s[i] = s[i + 1] * size[i + 1]
    return s


def geo_slice(ds, geo_dim, fixed):
    """Return {geo_code: (geo_label, value)} over the geography dimension,
    with the other dimensions pinned by {dim_id: category_label}."""
    ids, size = ds["id"], ds["size"]
    strides = _strides(size)
    geo_axis = ids.index(geo_dim)
    cat = ds["dimension"][geo_dim]["category"]
    gidx = cat["index"]
    pos2code = ({p: c for c, p in gidx.items()} if isinstance(gidx, dict)
                else dict(enumerate(gidx)))
    fixed_pos = {ids.index(d): _pos_of(ds["dimension"][d], lbl) for d, lbl in fixed.items()}
    values = ds["value"]
    out = {}
    for gp in range(size[geo_axis]):
        sel = [0] * len(ids)
        for ax, p in fixed_pos.items():
            sel[ax] = p
        sel[geo_axis] = gp
        flat = sum(p * stride for p, stride in zip(sel, strides))
        v = values.get(str(flat)) if isinstance(values, dict) else values[flat]
        code = pos2code[gp]
        out[code] = (cat["label"][code], v)
    return out


def rate(carers, pop):
    return round(100 * carers / pop, 3) if carers is not None and pop else None


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {path.relative_to(ROOT)}  ({len(rows)} rows)")


def build_nuts3():
    carers = geo_slice(fetch("SAP2022T12T2NUTS"), NUTS3, {SEX: "Both Sexes"})
    pop = geo_slice(fetch("SAP2022T1T1NUTS"), NUTS3, {SEX: "Both Sexes", AGE: "Total"})
    rows = []
    for code, (name, c) in carers.items():
        _, p = pop.get(code, (None, None))
        rows.append([code, name, c, p, rate(c, p)])
    rows.sort(key=lambda r: (r[4] is None, -(r[4] or 0)))
    write_csv(OUT / "carer_rate_nuts3.csv",
              ["nuts3_code", "region", "carers", "population", "carer_rate_pct"], rows)


def build_small_area():
    # All Small-Area tables share dimension C04172V04943, so the category code
    # (a GUID) is a stable, exact join key across every layer below.
    carers = geo_slice(fetch("SAP2022T12T2SA"), SA, {SEX: "Both Sexes"})
    pop = geo_slice(fetch("SAP2022T1T1SA"), SA, {SEX: "Both Sexes", AGE: "Total"})
    hh = fetch("SAP2022T5T1SA")
    hh_one = geo_slice(hh, SA, {"STATISTIC": "Private households", HH: "One person"})
    hh_tot = geo_slice(hh, SA, {"STATISTIC": "Private households", HH: "Total"})
    car = fetch("SAP2022T15T1SA")
    nocar = geo_slice(car, SA, {CAR: "No motor car"})
    car_tot = {}
    for band in CAR_BANDS:
        for g, (_, v) in geo_slice(car, SA, {CAR: band}).items():
            car_tot[g] = car_tot.get(g, 0) + (v or 0)

    rows = []
    for g, (name, c) in carers.items():
        if name.strip().lower() == "ireland":  # state aggregate, not a small area
            continue
        _, p = pop.get(g, (None, None))
        _, one = hh_one.get(g, (None, None))
        _, tot = hh_tot.get(g, (None, None))
        _, nc = nocar.get(g, (None, None))
        ct = car_tot.get(g)
        rows.append([name, c, p, rate(c, p),
                     one, tot, rate(one, tot),
                     nc, ct, rate(nc, ct)])
    rows.sort(key=lambda r: r[0])
    write_csv(OUT / "carer_at_risk_small_area.csv",
              ["sa_2022_code", "carers", "population", "carer_rate_pct",
               "one_person_hh", "total_hh", "one_person_hh_pct",
               "no_car_hh", "total_hh_cars", "no_car_hh_pct"], rows)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    print("NUTS3 (base map):")
    build_nuts3()
    print("Small area (zoom layer):")
    build_small_area()
