#!/usr/bin/env python3
"""Capstone — "target your supply here". Joins the three scored layers into one
operator-facing drill-down: the 20 HSE areas ranked by Market Gap, each expanded to
its worst service-desert small areas (the towns to target first).

No new index, no new modelling — every number is already locked in the source CSVs.
This is a join + a presentation file:

  data/iha_market_gap.csv     20 IHAs ranked by need-vs-provider gap (Plan 4)
  data/sa_service_desert.csv  per-SA service desert + nearest-support + precision flag
  data/sa_to_iha.csv          SA -> IHA crosswalk (join on sa_2022_code, 0 unassigned)
  site/sa/*.geojson           SA centroids (for map pins), via build_service_desert
  data/sa_town_names.csv      OPTIONAL sa_2022_code -> human town name (separate chat;
                              see docs/TOWN_NAMING_BRIEF.md). Falls back to the SA code.

Output: data/target_drilldown.json + site/iha/target_drilldown.json (served copy)
  [ {iha_code, iha_name, rank, market_gap_score, mean_vulnerability, provider_count,
     providers_per_1k_65plus, towns: [ {sa, town, desert, vulnerability, d_nearest_km,
     nearest_type, nearest_loc, lat, lon} ] } ]  sorted by rank (1 = enter first)
"""
import csv
import json
from pathlib import Path

from build_service_desert import load_sa_geometry

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE_IHA = ROOT / "site" / "iha"

M_TOWNS = 10   # worst-desert small areas listed per IHA


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load_town_names():
    path = DATA / "sa_town_names.csv"
    if not path.exists():
        return {}
    return {r["sa_2022_code"]: (r.get("town_name", "").strip(),
                                r.get("town_name_alt", "").strip(),
                                fnum(r.get("distance_km")))
            for r in csv.DictReader(path.open())}


def main():
    # SA centroids for the map pins (reuse Plan 3's geometry loader)
    _, _, records = load_sa_geometry()
    centroid = {code: (round(lon, 5), round(lat, 5))
                for (_region, _idx, code, lon, lat) in records}

    desert = {r["sa_2022_code"]: r
              for r in csv.DictReader((DATA / "sa_service_desert.csv").open())}
    iha_of = {r["sa_2022_code"]: r["IHA_code"]
              for r in csv.DictReader((DATA / "sa_to_iha.csv").open())}
    gap = {r["iha_code"]: r
           for r in csv.DictReader((DATA / "iha_market_gap.csv").open())}
    towns = load_town_names()

    # group desert SAs by their IHA
    by_iha = {}
    for code, r in desert.items():
        ih = iha_of.get(code)
        if ih is not None:
            by_iha.setdefault(ih, []).append((code, r))

    out = []
    for code, g in sorted(gap.items(), key=lambda kv: int(kv[1]["rank"])):
        sas = by_iha.get(code, [])
        sas.sort(key=lambda cr: -(fnum(cr[1]["service_desert"]) or 0))
        top = []
        for sa_code, r in sas[:M_TOWNS]:
            lon, lat = centroid.get(sa_code, (None, None))
            town, town_alt, town_km = towns.get(sa_code, ("", "", None))
            top.append({
                "sa": sa_code,
                "town": town or f"SA {sa_code}",   # filled by naming chat
                "town_alt": town_alt,              # English name for Irish-named places
                "town_km": town_km,                # SA->town distance; UI says "near" if small
                "desert": fnum(r["service_desert"]),
                "vulnerability": fnum(r["vulnerability"]),
                "d_nearest_km": fnum(r["d_nearest_km"]),
                "nearest_type": r["nearest_type"],
                "nearest_loc": r["nearest_loc"],     # geocode precision flag (honesty)
                "lat": lat, "lon": lon,
            })
        out.append({
            "iha_code": code,
            "iha_name": g["iha_name"],
            "rank": int(g["rank"]),
            "market_gap_score": fnum(g["market_gap_score"]),
            "mean_vulnerability": fnum(g["mean_vulnerability"]),
            "provider_count": int(g["provider_count"]),
            "providers_per_1k_65plus": fnum(g["providers_per_1k_65plus"]),
            "towns": top,
        })

    blob = json.dumps(out, separators=(",", ":"))
    (DATA / "target_drilldown.json").write_text(blob)
    SITE_IHA.mkdir(parents=True, exist_ok=True)
    (SITE_IHA / "target_drilldown.json").write_text(blob)

    named = sum(1 for iha in out for t in iha["towns"] if not t["town"].startswith("SA "))
    total = sum(len(iha["towns"]) for iha in out)
    print(f"  wrote target_drilldown.json ({len(out)} IHAs, {total} target towns, "
          f"{named} with real names, {total - named} awaiting sa_town_names.csv)")
    print("\nTop 3 IHAs to enter, with their worst-desert towns:")
    for iha in out[:3]:
        print(f"  #{iha['rank']} {iha['iha_name']}  gap {iha['market_gap_score']:+.0f}, "
              f"{iha['provider_count']} providers")
        for t in iha["towns"][:3]:
            flag = "" if t["nearest_loc"] == "address" else f" [~{t['nearest_loc']}]"
            print(f"       {t['town']:24s} desert {t['desert']:.0f}  "
                  f"{t['d_nearest_km']:.0f} km to {t['nearest_type']}{flag}")


if __name__ == "__main__":
    main()
