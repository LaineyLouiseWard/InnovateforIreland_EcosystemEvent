#!/usr/bin/env python3
"""Fetch the Pobal HP Deprivation score (Strain theme) and assign it to each
small area via the SA -> Electoral Division crosswalk (Plan 1).

The deprivation index is only released at ED level — SA-level scores are gated.
SAs nest cleanly within EDs, so each SA inherits its parent ED's relative
deprivation score. Within-ED variation is lost; the inter-ED signal (the main
one) is preserved. ~5 SAs per ED — fine for a prototype, flagged as "assigned
from parent ED" in the methodology.

Sources (keyless, open):
  Pobal HP Deprivation Index 2022, ED scores (CC-BY 4.0)
    https://www.pobal.ie/wp-content/uploads/2024/01/hp-deprivation-index-scores-2022.csv
  CSO Small Area 2022 boundaries (Tailte Eireann, ArcGIS) — SA -> ED crosswalk
    attribute query for SA_PUB2022 + ED_ID_STR (no geometry)
Accessed: 2026-06-08

Join key : ED_ID_STR (6-digit ED code, present in both files).
Score    : Index22_ED_std_rel_wt (relative HP index; negative = more deprived).

Output: data/pobal_ed_deprivation.csv  (one row per small area:
        sa_pub2022, ed_id_str, ed_name, deprivation_score)
"""
import csv
import json
import urllib.request
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data"

POBAL_URL = "https://www.pobal.ie/wp-content/uploads/2024/01/hp-deprivation-index-scores-2022.csv"
SCORE_COL = "Index22_ED_std_rel_wt"   # relative HP deprivation score (headline)


def norm_ed(code):
    """ED_ID_STR join key. Pobal drops leading zeros on ~1,400 EDs ('17001') where
    the ArcGIS boundary keeps them ('017001'); stripping zeros on both sides makes
    the join exact (3,417/3,417 EDs). Composite codes ('027014/027038') match as-is."""
    return str(code).strip().lstrip("0")

ARCGIS = ("https://services-eu1.arcgis.com/BuS9rtTsYEV5C0xh/ArcGIS/rest/services/"
          "SMALL_AREA_2022_Genralised_20m_view/FeatureServer/0/query")
PAGE = 2000


def fetch_pobal():
    dest = RAW / "pobal_deprivation.csv"
    if not dest.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        print("  fetching Pobal deprivation CSV ...")
        urllib.request.urlretrieve(POBAL_URL, dest)
    scores = {}
    for row in csv.DictReader(dest.open(encoding="latin-1")):  # Irish ED names, cp1252/latin-1
        ed = norm_ed(row["ED_ID_STR"])
        try:
            scores[ed] = (round(float(row[SCORE_COL]), 2), row["ED_ENGLISH"].strip())
        except (KeyError, ValueError):
            continue
    return scores


def fetch_crosswalk():
    """SA_PUB2022 -> ED_ID_STR for all small areas (attributes only, no geometry)."""
    dest = RAW / "sa_ed_crosswalk.json"
    if dest.exists():
        return json.loads(dest.read_text())
    rows, off = [], 0
    while True:
        q = urllib.parse.urlencode({"where": "1=1",
            "outFields": "SA_PUB2022,ED_ID_STR,ED_ENGLISH",
            "returnGeometry": "false", "resultOffset": off,
            "resultRecordCount": PAGE, "f": "json"})
        with urllib.request.urlopen(f"{ARCGIS}?{q}", timeout=180) as r:
            d = json.load(r)
        page = [f["attributes"] for f in d.get("features", [])]
        rows.extend(page)
        print(f"  crosswalk: {len(rows)} / 18919")
        if len(page) < PAGE:
            break
        off += PAGE
    RAW.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rows))
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    scores = fetch_pobal()
    crosswalk = fetch_crosswalk()
    print(f"  {len(scores)} EDs scored, {len(crosswalk)} small areas")

    rows, unmatched = [], 0
    for a in crosswalk:
        ed = str(a["ED_ID_STR"]).strip()
        hit = scores.get(norm_ed(ed))
        if hit is None:
            unmatched += 1
            score, ed_name = None, a.get("ED_ENGLISH", "")
        else:
            score, ed_name = hit
        rows.append([a["SA_PUB2022"], ed, ed_name, score])
    rows.sort(key=lambda r: r[0])

    with (OUT / "pobal_ed_deprivation.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sa_pub2022", "ed_id_str", "ed_name", "deprivation_score"])
        w.writerows(rows)
    print(f"  wrote data/pobal_ed_deprivation.csv ({len(rows)} SAs, "
          f"{unmatched} without an ED score)")


if __name__ == "__main__":
    main()
