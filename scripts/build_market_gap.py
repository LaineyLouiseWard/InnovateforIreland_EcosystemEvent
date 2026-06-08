#!/usr/bin/env python3
"""Plan 4 — Market Gap Score, aggregated to the 20 HSE Integrated Healthcare
Areas (IHAs). The operator/investor view: which service area has the most unmet
demand per approved provider?

Method (defaults locked with the project lead):
  demand     = population-weighted mean of Plan 1's per-SA vulnerability_score,
               rolled up via data/sa_to_iha.csv
  supply     = count of distinct approved home-support providers per IHA, parsed
               straight from the 20 HSE provider-list PDFs (data/raw/iha/*.pdf).
               This needs no geocoding — each PDF *is* one IHA.
  density    = providers per 1,000 people aged 65+ (per-65+ denominator)
  Market Gap = PR(mean vulnerability) − PR(provider density)   [rank difference]
               percentile ranks across the 20 IHAs, range -100..+100; higher =
               more need relative to supply = larger market opportunity. (A
               difference, not a ratio — a ratio blows up on the lowest-density
               IHA and is not a meaningful magnitude.)
  No Fair Deal viability adjustment in v1.

Inputs : data/sa_vulnerability.csv, data/sa_demographics.csv, data/sa_to_iha.csv,
         data/boundaries/iha_2025.geojson, data/raw/iha/*.pdf
Outputs: data/iha_market_gap.csv               ranked IHA table (the CSV export)
         site/iha/iha_market_gap.geojson        polygons + scores for the map
         site/iha/_meta.json                    choropleth breaks
"""
import bisect
import csv
import importlib.util
import json
import re
import time
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PDF_DIR = DATA / "raw" / "iha"
IHA_GEO = DATA / "boundaries" / "iha_2025.geojson"
OUT_CSV = DATA / "iha_market_gap.csv"
OUT_GEO = ROOT / "site" / "iha" / "iha_market_gap.geojson"
OUT_META = ROOT / "site" / "iha" / "_meta.json"

# PDF filename signature (normalised, alnum-lowercase) -> IHA_code. Ordered most
# specific first so substring matches are unambiguous (the Dublin/Wicklow ones).
PDF_TO_IHA = [
    ("dublinnorthcity", "22"), ("dublinnorthcounty", "23"),
    ("dublinsouthcity", "11"), ("dublinsouthwest", "12"),
    ("dublinsouthwicklow", "32"), ("kildarewestwicklow", "13"),
    ("carlow", "31"), ("cavan", "21"), ("clarelimerick", "41"),
    ("corknorth", "51"), ("corksouth", "52"), ("donegal", "61"),
    ("galwayroscommon", "62"), ("kerry", "53"), ("limerickcity", "42"),
    ("louthmeath", "24"), ("mayo", "63"), ("midlands", "14"),
    ("sligoleitrim", "64"), ("waterfordwexford", "33"),
]


def percentile_ranks(pairs):
    """{key: percentile rank 0-100}, tie-aware mid-rank, higher value -> higher rank.
    Same method as build_vulnerability_index.py."""
    items = [(k, v) for k, v in pairs if v is not None]
    svals = sorted(v for _, v in items)
    n = len(items)
    out = {}
    for k, v in items:
        lo = bisect.bisect_left(svals, v)
        hi = bisect.bisect_right(svals, v)
        out[k] = round(100 * ((lo + hi) / 2) / n, 2)
    return out


def round_coords(obj, nd=5):
    if isinstance(obj, (int, float)):
        return round(obj, nd)
    return [round_coords(x, nd) for x in obj]


# --- reuse the careful PDF table parser from fetch_supply.py, without triggering
# its module-level geocode-cache read (that file is being rewritten live).
def load_parser():
    src = (Path(__file__).parent / "fetch_supply.py").read_text()
    # keep only the parser + its regex helpers; drop everything geocode/network.
    ns = {"fitz": fitz, "re": re}
    exec("import re\nWEB = re.compile(r'www\\.[^\\s|]+', re.I)\n"
         "EIRCODE = re.compile(r'\\b([AC-FHKNPRTV-Y][0-9]{2}\\s?[0-9AC-FHKNPRTV-Y]{4})\\b')",
         ns)
    m = re.search(r"def parse_iha_pdf\(path\):.*?\n    return recs\n", src, re.S)
    exec(m.group(0), ns)
    m2 = re.search(r"def parse_town\(address\):.*?\n    return parts\[-1\] if parts else \"\"\n", src, re.S)
    exec(m2.group(0), ns)
    return ns["parse_iha_pdf"], ns["parse_town"], ns["EIRCODE"]


def map_pdf(path):
    norm = re.sub(r"[^a-z0-9]", "", path.stem.lower())
    for sig, code in PDF_TO_IHA:
        if sig in norm:
            return code
    return None


def provider_counts():
    parse_iha_pdf, parse_town, EIRCODE = load_parser()
    by_iha = {}
    for pdf in sorted(PDF_DIR.glob("*.pdf")):
        code = map_pdf(pdf)
        if code is None:
            print(f"  WARN unmatched PDF: {pdf.name}")
            continue
        by_iha.setdefault(code, []).append(pdf)
    counts = {}
    for code, pdfs in by_iha.items():
        seen = set()
        for pdf in pdfs:                       # merges any duplicate file for an IHA
            for r in parse_iha_pdf(pdf):
                town = parse_town(r["address"])
                key = r["eircode"] or f"{r['provider'].lower()}|{town.lower()}"
                seen.add(key)
        counts[code] = len(seen)
    return counts


def load_sa():
    vuln = {r["sa_2022_code"]: float(r["vulnerability_score"])
            for r in csv.DictReader(open(DATA / "sa_vulnerability.csv"))
            if r["vulnerability_score"]}
    demo = {}
    for r in csv.DictReader(open(DATA / "sa_demographics.csv")):
        demo[r["sa_2022_code"]] = (int(float(r["population"] or 0)),
                                   int(float(r["pop_65plus"] or 0)))
    xwalk = {r["sa_2022_code"]: (r["IHA_code"], r["IHA_operational_name"],
                                 r["HR_operational_name"])
             for r in csv.DictReader(open(DATA / "sa_to_iha.csv"))}
    return vuln, demo, xwalk


def pct(vals, q):
    """Linear-interpolated q-quantile (q in 0..1) of non-null values."""
    s = sorted(x for x in vals if x is not None)
    if not s:
        return None
    i = q * (len(s) - 1)
    lo = int(i)
    hi = min(lo + 1, len(s) - 1)
    return round(s[lo] + (s[hi] - s[lo]) * (i - lo), 1)


def iha_spread():
    """Per-IHA internal spread of the FINAL (distance-aware) vulnerability shown on the
    SA map — from sa_service_desert.csv, not the demand-only sa_vulnerability.csv — plus
    a count of each IHA's SAs in the national top decile. Drives the spread bar + the
    hidden-hotspot badge. Returns {iha_code: {vP05, vP95, vTop10, nSA}} or {} if the
    desert layer isn't built yet."""
    path = DATA / "sa_service_desert.csv"
    if not path.exists():
        return {}
    sd = {r["sa_2022_code"]: float(r["vulnerability"])
          for r in csv.DictReader(open(path)) if r["vulnerability"]}
    xwalk = {r["sa_2022_code"]: r["IHA_code"]
             for r in csv.DictReader(open(DATA / "sa_to_iha.csv"))}
    p90 = pct(list(sd.values()), 0.9)
    by = {}
    for sa, v in sd.items():
        ih = xwalk.get(sa)
        if ih is not None:
            by.setdefault(ih, []).append(v)
    return {ih: {"vP05": pct(vs, 0.05), "vP95": pct(vs, 0.95),
                 "vTop10": sum(1 for v in vs if p90 is not None and v >= p90),
                 "nSA": len(vs)}
            for ih, vs in by.items()}


def main():
    vuln, demo, xwalk = load_sa()
    counts = provider_counts()
    spread = iha_spread()

    agg = {}  # code -> dict
    for sa, (code, name, hr) in xwalk.items():
        if sa not in vuln or sa not in demo:
            continue
        pop, p65 = demo[sa]
        a = agg.setdefault(code, {"name": name, "hr": hr, "sa": 0, "pop": 0,
                                  "p65": 0, "wsum": 0.0})
        a["sa"] += 1
        a["pop"] += pop
        a["p65"] += p65
        a["wsum"] += vuln[sa] * pop          # population-weighted

    for code, a in agg.items():
        a["vuln"] = a["wsum"] / a["pop"] if a["pop"] else 0.0
        a["providers"] = counts.get(code, 0)
        a["dens"] = a["providers"] / a["p65"] * 1000 if a["p65"] else 0.0  # per 1k 65+

    pr_v = percentile_ranks([(c, a["vuln"]) for c, a in agg.items()])
    pr_d = percentile_ranks([(c, a["dens"]) for c, a in agg.items()])
    for code, a in agg.items():
        a["pr_v"] = pr_v[code]
        a["pr_d"] = pr_d[code]
        # Difference of percentile ranks, not a ratio: bounded [-100, +100], linear,
        # and stable. A ratio explodes when the denominator is the lowest-density IHA
        # (Kerry's PR_density ~2.5 -> score 33, an artifact). Standardised-score
        # differencing is the recognised method for need-vs-provision indices.
        a["gap"] = round(a["pr_v"] - a["pr_d"], 1)          # +100 = most need, least supply

    ranked = sorted(agg.items(), key=lambda kv: kv[1]["gap"], reverse=True)
    for rank, (code, a) in enumerate(ranked, 1):
        a["rank"] = rank

    # ---- CSV (the operator export) ----
    cols = ["iha_code", "iha_name", "health_region", "sa_count", "population",
            "pop_65plus", "mean_vulnerability", "provider_count",
            "providers_per_1k_65plus", "pr_vulnerability", "pr_provider_density",
            "market_gap_score", "rank"]
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for code, a in ranked:
            w.writerow([code, a["name"], a["hr"], a["sa"], a["pop"], a["p65"],
                        round(a["vuln"], 2), a["providers"], round(a["dens"], 3),
                        a["pr_v"], a["pr_d"], a["gap"], a["rank"]])
    print(f"  wrote {OUT_CSV.relative_to(ROOT)}")

    # ---- site GeoJSON (polygons + scores) ----
    fc = json.loads(IHA_GEO.read_text())
    gaps = []
    for ft in fc["features"]:
        code = ft["properties"]["IHA_code"]
        a = agg.get(code)
        if not a:
            continue
        gaps.append(a["gap"])
        ft["geometry"]["coordinates"] = round_coords(ft["geometry"]["coordinates"])
        ft["properties"] = {"code": code, "name": a["name"], "hr": a["hr"],
                            "gap": a["gap"], "vuln": round(a["vuln"], 1),
                            "providers": a["providers"],
                            "dens": round(a["dens"], 2),
                            "pop65": a["p65"], "rank": a["rank"],
                            **spread.get(code, {})}   # vP05, vP95, vTop10, nSA
    OUT_GEO.parent.mkdir(parents=True, exist_ok=True)
    OUT_GEO.write_text(json.dumps(fc, separators=(",", ":")))

    sg = sorted(gaps)
    breaks = [round(sg[int(len(sg) * i / 5)], 3) for i in range(1, 5)]
    OUT_META.write_text(json.dumps({
        "n": len(gaps), "breaks": breaks,
        "measure": "Market Gap Score = PR(vulnerability) − PR(provider density per 1k 65+)",
        "note": "20 HSE Integrated Healthcare Areas. Range -100 to +100; higher = more "
                "demand than approved home-support supply (need rank above supply rank). "
                "Percentile ranks across the 20 IHAs; a difference, not a ratio, so the "
                "magnitude is comparable and stable."},
        indent=1))
    print(f"  wrote {OUT_GEO.relative_to(ROOT)} and {OUT_META.relative_to(ROOT)}")

    print(f"\n  {'#':>2}  {'IHA':<44} {'vuln':>5} {'prov':>4} {'/1k65':>6} {'gap':>6}")
    for code, a in ranked:
        print(f"  {a['rank']:>2}  {a['name']:<44} {a['vuln']:>5.1f} "
              f"{a['providers']:>4} {a['dens']:>6.2f} {a['gap']:>6.2f}")


if __name__ == "__main__":
    main()
