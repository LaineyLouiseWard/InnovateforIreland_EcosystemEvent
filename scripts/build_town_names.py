#!/usr/bin/env python3
"""Map every 2022 Small Area code to the human place it's near, so the capstone
drill-down can say "near Listowel, Co. Kerry" instead of "SA 077128019".

Single authoritative source, keyless: the CSO/Tailte Small Area 2022 layer already
tags each SA with the named CSO Settlement it sits inside (SA_URBAN_AREA_NAME) and
its county (COUNTY_ENGLISH). 13,185 of 18,919 SAs are inside a named settlement; the
rest are rural. So:

  * inside a settlement  -> that settlement's name           (method within_settlement)
  * rural (no settlement) -> the nearest settlement centroid  (method nearest_settlement)

Settlement centroids are derived from the member SAs of each named settlement (mean
of their centroids) — no extra download, no API key, same source as everything else.

Nearest-settlement is constrained to the SA's own (traditional) county. Straight-line
distance otherwise lies across water: e.g. a Loop Head SA in Clare is 13 km from
Ballybunion as the crow flies but a ~100 km drive (around the Shannon estuary, and in
Co. Kerry) — so "Ballybunion, Clare" was both unreachable and a county mismatch. Same-
county keeps town_name consistent with county and with the IHA an operator works in.
distance_km is always SA-centroid -> named-settlement-centroid, so a far rural match is
auditable (the UI footnotes "near" when far; it's the nearest settlement, not an address).

Gaeltacht settlements are stored under their official CSO Irish name; town_name_alt
carries the common English/anglicised name (Belmullet for Béal An Mhuirthead, etc.) so
the place is findable both ways. English aliases verified against logainm.ie.

Output: data/sa_town_names.csv
  (sa_2022_code, town_name, town_name_alt, county, method, distance_km)
Downstream: scripts/build_target_drilldown.py reads it if present and joins on
sa_2022_code, falling back to the raw code when a name is missing.

Source: Tailte Eireann / CSO "Small Area 2022 (Generalised 20m)", attribute table only
(no geometry), via the same ArcGIS FeatureServer used by fetch_sa_boundaries.py.
Accessed 2026-06-08. Raw attribute pull cached to the gitignored data/raw/.
"""
import csv
import json
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

import numpy as np

from build_service_desert import load_sa_geometry, EARTH_KM
from fetch_sa_boundaries import canon

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ATTR_CACHE = DATA / "raw" / "sa_attributes.json"

ATTR_URL = ("https://services-eu1.arcgis.com/BuS9rtTsYEV5C0xh/ArcGIS/rest/services/"
            "SMALL_AREA_2022_Genralised_20m_view/FeatureServer/0/query")
ATTR_FIELDS = "SA_PUB2022,SA_URBAN_AREA_NAME,COUNTY_ENGLISH"
PAGE = 2000

# COUNTY_ENGLISH splits cities from their county; merge to the traditional county so the
# same-county nearest-settlement search can still reach a city SA from its rural fringe.
TRAD_COUNTY = {
    "CORK CITY": "CORK", "GALWAY CITY": "GALWAY", "LIMERICK CITY": "LIMERICK",
    "WATERFORD CITY": "WATERFORD", "NORTH TIPPERARY": "TIPPERARY",
    "SOUTH TIPPERARY": "TIPPERARY", "DUBLIN CITY": "DUBLIN", "SOUTH DUBLIN": "DUBLIN",
    "FINGAL": "DUBLIN", "DUN LAOGHAIRE/RATHDOWN": "DUBLIN",
}

# Common English / anglicised names for the CSO's Irish-only settlement names, so a
# search for "Belmullet" finds Béal An Mhuirthead. Keys match SA_URBAN_AREA_NAME exactly;
# every English form verified on logainm.ie (the official Placenames Database of Ireland).
ENGLISH_ALIAS = {
    "Ailt An Chorráin": "Burtonport", "An Bun Beag": "Bunbeg", "An Charraig": "Carrick",
    "An Cheathrú Rua": "Carraroe", "An Clochán Liath": "Dungloe",
    "An Fál Carrach": "Falcarragh", "An Rinn": "Ring", "An Spidéal": "Spiddal",
    "Baile Chláir": "Claregalway", "Baile Mhic Íre": "Ballymakeery",
    "Bun Na Leaca": "Brinlack", "Béal An Mhuirthead": "Belmullet",
    "Béal Átha An Ghaorthaidh": "Ballingeary", "Cill Rónáin": "Kilronan",
    "Cluain Bú": "Cloonboo", "Dingle-Daingean Uí Chuis": "Dingle",
    "Doirí Beaga": "Derrybeg", "Dumha Thuama": "Doohoma", "Gob an Choire": "Achill Sound",
    "Gort An Choirce": "Gortahork", "Loch An Iúir": "Loughanure",
    "Mín Lárach": "Meenlaragh", "Na Dúnaibh": "Downings", "Na Forbacha": "Furbo",
    "Rann Na Feirste": "Rannafast",
}


def fetch_attributes():
    """SA code -> {settlement name, county}, attribute table only (no geometry).
    Cached to the gitignored data/raw/ so it's re-pulled, not committed."""
    if ATTR_CACHE.exists():
        print(f"  using cached {ATTR_CACHE.relative_to(ROOT)}")
        return json.loads(ATTR_CACHE.read_text())
    rows, off = [], 0
    while True:
        q = urllib.parse.urlencode({"where": "1=1", "outFields": ATTR_FIELDS,
                                    "returnGeometry": "false", "resultOffset": off,
                                    "resultRecordCount": PAGE, "f": "json"})
        with urllib.request.urlopen(f"{ATTR_URL}?{q}", timeout=180) as r:
            d = json.load(r)
        page = d.get("features", [])
        rows.extend(a["attributes"] for a in page)
        if len(page) < PAGE:
            break
        off += PAGE
    ATTR_CACHE.parent.mkdir(parents=True, exist_ok=True)
    ATTR_CACHE.write_text(json.dumps(rows))
    print(f"  fetched {len(rows)} SA attribute rows -> {ATTR_CACHE.relative_to(ROOT)}")
    return rows


def tidy_county(name):
    """COUNTY_ENGLISH is upper-case admin county, e.g. 'DUN LAOGHAIRE/RATHDOWN'."""
    return (name or "").title().replace("/", "-").strip()


def haversine(lon1, lat1, lon2, lat2):
    rlat1, rlat2 = np.radians(lat1), np.radians(lat2)
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) ** 2 + np.cos(rlat1) * np.cos(rlat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_KM * np.arcsin(np.sqrt(a))


def main():
    attrs = {canon(a["SA_PUB2022"]): a for a in fetch_attributes()}

    # SA centroids (reuse Plan 3's loader); records: (region, idx, code, lon, lat)
    _, _, records = load_sa_geometry()
    cent = {code: (lon, lat) for (_r, _i, code, lon, lat) in records}
    trad = {code: TRAD_COUNTY.get(a.get("COUNTY_ENGLISH"), a.get("COUNTY_ENGLISH"))
            for code, a in attrs.items()}

    # derived settlement centroid = mean of member-SA centroids; settlement county = modal
    groups = {}
    for code, a in attrs.items():
        name = (a.get("SA_URBAN_AREA_NAME") or "").strip()
        if name and code in cent:
            groups.setdefault(name, []).append(code)
    names = list(groups)
    sidx = {n: i for i, n in enumerate(names)}
    slon = np.array([np.mean([cent[c][0] for c in groups[n]]) for n in names])
    slat = np.array([np.mean([cent[c][1] for c in groups[n]]) for n in names])
    scounty = np.array([Counter(trad[c] for c in groups[n]).most_common(1)[0][0]
                        for n in names])

    rural = [c for c in cent if not (attrs.get(c, {}).get("SA_URBAN_AREA_NAME") or "").strip()]
    rlon = np.array([cent[c][0] for c in rural])
    rlat = np.array([cent[c][1] for c in rural])
    # distance to every settlement, then block out other counties before taking the min
    dist = haversine(rlon[:, None], rlat[:, None], slon[None, :], slat[None, :])
    same = scounty[None, :] == np.array([trad[c] for c in rural])[:, None]
    dist = np.where(same, dist, np.inf)
    nearest_i = dist.argmin(axis=1)
    nearest_d = dist.min(axis=1)
    nearest = {c: (names[nearest_i[k]], float(nearest_d[k])) for k, c in enumerate(rural)}

    out = []
    for code in cent:
        a = attrs.get(code, {})
        own = (a.get("SA_URBAN_AREA_NAME") or "").strip()
        if own:
            town, method = own, "within_settlement"
            d = haversine(*cent[code], slon[sidx[own]], slat[sidx[own]])
        else:
            town, d = nearest[code]
            method = "nearest_settlement"
        out.append({"sa_2022_code": code, "town_name": town,
                    "town_name_alt": ENGLISH_ALIAS.get(town, ""),
                    "county": tidy_county(a.get("COUNTY_ENGLISH")),
                    "method": method, "distance_km": round(float(d), 2)})

    out.sort(key=lambda r: r["sa_2022_code"])
    with (DATA / "sa_town_names.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["sa_2022_code", "town_name", "town_name_alt",
                                          "county", "method", "distance_km"])
        w.writeheader()
        w.writerows(out)

    within = sum(1 for r in out if r["method"] == "within_settlement")
    aliased = sum(1 for r in out if r["town_name_alt"])
    print(f"  wrote sa_town_names.csv: {len(out)} SAs named "
          f"({within} within a settlement, {len(out) - within} nearest-settlement), "
          f"{len(names)} settlements, {aliased} SAs with an English alias")

    # confirm the capstone's ~200 priority SAs are all named
    targets = [t["sa"] for iha in json.loads((DATA / "target_drilldown.json").read_text())
               for t in iha["towns"]]
    by = {r["sa_2022_code"]: r for r in out}
    missing = [c for c in targets if c not in by]
    print(f"  priority targets: {len(targets) - len(missing)}/{len(targets)} named"
          + (f"  MISSING: {missing}" if missing else ""))
    far = sorted({c: by[c] for c in targets if c in by and by[c]["distance_km"] > 10}.values(),
                 key=lambda r: -r["distance_km"])
    if far:
        print(f"  {len(far)} target(s) >10 km from their named town — genuinely remote, "
              f"UI shows 'nearest town: X (N km)':")
        for r in far[:5]:
            alt = f" ({r['town_name_alt']})" if r["town_name_alt"] else ""
            print(f"     {r['sa_2022_code']}  {r['town_name']}{alt}, {r['county']} "
                  f"({r['distance_km']:.0f} km)")


if __name__ == "__main__":
    main()
