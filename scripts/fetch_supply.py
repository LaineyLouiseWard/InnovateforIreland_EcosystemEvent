#!/usr/bin/env python3
"""Plan 2 — care-supply overlay. Builds three point layers of where carer/older-person
support physically exists, to sit on top of the Plan 1 vulnerability choropleth.

  Nursing homes     HIQA Register of Designated Centres for Older People (live CSV)
  FCI centres       Family Carers Ireland support offices (curated data/fci_centres.json)
  Home care agencies 20 HSE Approved Home-Support Provider lists (PDFs)

All sources are keyless, open, Republic of Ireland. Addresses are geocoded with OSM
Nominatim (keyless, 1 req/s) — Eircodes are not openly geocodable, so we resolve the
textual address and fall back to town/county. Results cache to data/raw/, so re-runs
are instant and the slow geocoding only happens once.

Sources (accessed 2026-06-08):
  HIQA  https://www.hiqa.ie/centre/export/older_persons_register.csv?_format=csv
  HSE   https://www2.hse.ie/services/home-support-service/choosing-an-approved-provider/
  FCI   https://www.familycarers.ie/carer-supports/get-support/  (-> data/fci_centres.json)

Outputs (committed, in data/):
  nursing_homes.geojson  fci_centres.geojson  homecare_agencies.geojson
  supply_meta.json       counts + geocoding precision summary
"""
import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DATA = ROOT / "data"
IHA_DIR = RAW / "iha"
SITE_SUPPLY = ROOT / "site" / "supply"   # served copy for the Leaflet page

HIQA_CSV = "https://www.hiqa.ie/centre/export/older_persons_register.csv?_format=csv"
IHA_INDEX = "https://www2.hse.ie/services/home-support-service/choosing-an-approved-provider/"
HSE_BASE = "https://www2.hse.ie"

UA = "InnovateForIreland-carer-map/1.0 (lainey.ward1@ucdconnect.ie; prototype)"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
GEO_CACHE = RAW / "geocode_cache.json"
RATE_S = 1.1   # Nominatim usage policy: max 1 request/second

EIRCODE = re.compile(r"\b([AC-FHKNPRTV-Y][0-9]{2}\s?[0-9AC-FHKNPRTV-Y]{4})\b")
WEB = re.compile(r"www\.[^\s|]+", re.I)
COUNTY = re.compile(r"\bCo\.?\s+([A-Z][a-zA-Z]+)\b")


# ----------------------------------------------------------------------------- geocoding
_cache = json.loads(GEO_CACHE.read_text()) if GEO_CACHE.exists() else {}
_last = [0.0]


def _nominatim(params):
    """One rate-limited Nominatim call, cached by full query. Returns (lat,lon) or None."""
    key = json.dumps(params, sort_keys=True)
    if key in _cache:
        hit = _cache[key]
        return tuple(hit) if hit else None
    dt = RATE_S - (time.time() - _last[0])
    if dt > 0:
        time.sleep(dt)
    q = urllib.parse.urlencode({**params, "format": "json", "limit": 1,
                                "countrycodes": "ie"})
    req = urllib.request.Request(f"{NOMINATIM}?{q}", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.load(r)
        _last[0] = time.time()
    except Exception as e:
        print(f"    nominatim error: {e}")
        res = []
    hit = ([round(float(res[0]["lat"]), 6), round(float(res[0]["lon"]), 6)]
           if res else None)
    _cache[key] = hit
    GEO_CACHE.write_text(json.dumps(_cache))
    return tuple(hit) if hit else None


def geocode(address, town, county):
    """Resolve a point with progressive fallback. Returns (lat, lon, precision)."""
    addr = EIRCODE.sub("", address).strip(" ,.")
    attempts = []
    if addr:
        attempts.append(("address", {"q": f"{addr}, Ireland"}))
    if town and county:
        attempts.append(("town", {"q": f"{town}, {county}, Ireland"}))
    elif town:
        attempts.append(("town", {"q": f"{town}, Ireland"}))
    if county:
        attempts.append(("county", {"q": f"County {county}, Ireland"}))
    for precision, params in attempts:
        hit = _nominatim(params)
        if hit:
            return hit[0], hit[1], precision
    return None, None, "none"


def feature(lat, lon, props):
    return {"type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
            "properties": props}


def write_geojson(path, feats):
    blob = json.dumps({"type": "FeatureCollection", "features": feats},
                      separators=(",", ":"))
    path.write_text(blob)
    SITE_SUPPLY.mkdir(parents=True, exist_ok=True)
    (SITE_SUPPLY / path.name).write_text(blob)   # mirror to the served site dir
    print(f"  wrote {path.relative_to(ROOT)} ({len(feats)} points)")


# ----------------------------------------------------------------------------- nursing homes
def parse_town(address):
    """Best-effort town = last comma-segment before the Eircode."""
    parts = [p.strip() for p in EIRCODE.sub("", address).split(",") if p.strip()]
    return parts[-1] if parts else ""


def build_nursing_homes():
    dest = RAW / "hiqa_older_persons_register.csv"
    if not dest.exists():
        print("  fetching HIQA register ...")
        req = urllib.request.Request(HIQA_CSV, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as r:
            dest.write_bytes(r.read())
    rows = list(csv.DictReader(dest.open(encoding="utf-8-sig")))
    feats, prec = [], {}
    for i, r in enumerate(rows, 1):
        addr, county = r["Centre_Address"].strip(), r["County"].strip()
        ec = EIRCODE.search(addr)
        lat, lon, p = geocode(addr, parse_town(addr), county)
        prec[p] = prec.get(p, 0) + 1
        if lat is None:
            continue
        feats.append(feature(lat, lon, {
            "name": r["Centre_Title"].strip(), "addr": addr, "county": county,
            "phone": r.get("Centre_Phone", "").strip(),
            "beds": r.get("Maximum_Occupancy", "").strip(),
            "eircode": ec.group(1) if ec else "", "loc": p}))
        if i % 50 == 0:
            print(f"    nursing homes {i}/{len(rows)} geocoded")
    write_geojson(DATA / "nursing_homes.geojson", feats)
    return {"source": len(rows), "mapped": len(feats), "precision": prec}


# ----------------------------------------------------------------------------- FCI centres
def build_fci():
    centres = json.loads((DATA / "fci_centres.json").read_text())["centres"]
    feats, prec = [], {}
    for c in centres:
        lat, lon, p = geocode(c["address"], c["town"], c["county"])
        prec[p] = prec.get(p, 0) + 1
        if lat is None:
            continue
        feats.append(feature(lat, lon, {
            "name": f"FCI {c['name']}", "addr": c["address"], "county": c["county"],
            "phone": c["phone"], "eircode": c["eircode"],
            "serves": ", ".join(c["serves"]), "loc": p}))
    write_geojson(DATA / "fci_centres.geojson", feats)
    return {"source": len(centres), "mapped": len(feats), "precision": prec}


# ----------------------------------------------------------------------------- home care agencies
def fetch_iha_pdfs():
    IHA_DIR.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(IHA_INDEX, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        html = r.read().decode("utf-8", "replace")
    links = sorted(set(re.findall(r'href="(/documents/\d+/[^"]+\.pdf)"', html)))
    paths = []
    for link in links:
        name = link.split("/")[-1]
        dest = IHA_DIR / name
        if not dest.exists():
            print(f"  fetching {name}")
            for attempt in range(4):
                try:
                    req = urllib.request.Request(HSE_BASE + link,
                                                 headers={"User-Agent": UA})
                    with urllib.request.urlopen(req, timeout=120) as r:
                        dest.write_bytes(r.read())
                    break
                except Exception as e:
                    print(f"    retry {attempt + 1}: {e}")
                    time.sleep(2 * (attempt + 1))
            time.sleep(0.6)   # be polite to the HSE server between downloads
        paths.append(dest)
    return paths


def parse_iha_pdf(path):
    """Reconstruct the 4-column table. Each record has one website token (right
    column) used as a vertical anchor; words are bucketed to the nearest anchor and
    split into columns by the header x-positions (address col starts at the 2nd
    'Provider' header token, then 'Telephone', then 'Website')."""
    recs = []
    for pg in fitz.open(path):
        words = pg.get_text("words")
        ws_hdr = [w for w in words if w[4] == "Website"]
        if not ws_hdr:
            continue
        hy = ws_hdr[0][1]
        line = sorted([w for w in words if abs(w[1] - hy) < 4], key=lambda w: w[0])
        prov_x = [w[0] for w in line if w[4] == "Provider"]
        x_addr = prov_x[1] if len(prov_x) > 1 else 178
        x_tel = next((w[0] for w in line if w[4] == "Telephone"), 574)
        x_web = next((w[0] for w in line if w[4] == "Website"), 685)
        anchors = sorted({round(w[1]) for w in words
                          if w[1] > hy + 4 and w[0] >= x_web - 30 and WEB.match(w[4])})
        if not anchors:
            continue
        buckets = {a: [] for a in anchors}
        for w in words:
            if w[1] <= hy + 4:
                continue
            a = min(anchors, key=lambda A: abs(A - w[1]))
            if abs(a - w[1]) <= 30:
                buckets[a].append(w)
        for a in anchors:
            b = sorted(buckets[a], key=lambda w: (w[1], w[0]))
            prov = " ".join(w[4] for w in b if w[2] < x_addr).strip()
            addr = " ".join(w[4] for w in b if x_addr <= w[0] < x_tel - 5).strip()
            tel = " ".join(w[4] for w in b if x_tel - 5 <= w[0] < x_web - 20).strip()
            web = " ".join(w[4] for w in b if w[0] >= x_web - 20 and WEB.match(w[4]))
            if not prov or not addr:
                continue
            ec = EIRCODE.search(addr)
            recs.append({"provider": prov, "address": addr, "phone": tel,
                         "website": web, "eircode": ec.group(1) if ec else ""})
    return recs


def build_agencies():
    paths = fetch_iha_pdfs()
    raw = []
    for p in paths:
        raw.extend(parse_iha_pdf(p))
    # dedupe offices listed in more than one county PDF: key on eircode, else provider+town
    seen, uniq = {}, []
    for r in raw:
        town = parse_town(r["address"])
        key = r["eircode"] or f"{r['provider'].lower()}|{town.lower()}"
        if key in seen:
            continue
        seen[key] = True
        r["town"] = town
        uniq.append(r)
    print(f"  {len(raw)} provider rows across {len(paths)} PDFs -> {len(uniq)} distinct offices")
    feats, prec = [], {}
    for i, r in enumerate(uniq, 1):
        cm = COUNTY.search(r["address"])
        county = cm.group(1) if cm else ""
        lat, lon, p = geocode(r["address"], r["town"], county)
        prec[p] = prec.get(p, 0) + 1
        if lat is None:
            continue
        feats.append(feature(lat, lon, {
            "name": r["provider"], "addr": r["address"], "county": county,
            "phone": r["phone"], "website": r["website"],
            "eircode": r["eircode"], "loc": p}))
        if i % 50 == 0:
            print(f"    agencies {i}/{len(uniq)} geocoded")
    write_geojson(DATA / "homecare_agencies.geojson", feats)
    return {"source_rows": len(raw), "distinct": len(uniq),
            "mapped": len(feats), "precision": prec}


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    print("Nursing homes (HIQA):")
    nh = build_nursing_homes()
    print("FCI centres:")
    fci = build_fci()
    print("Home care agencies (HSE IHA PDFs):")
    ag = build_agencies()
    meta = {"nursing_homes": nh, "fci_centres": fci, "homecare_agencies": ag,
            "geocoder": "OSM Nominatim", "roi_only": True}
    (DATA / "supply_meta.json").write_text(json.dumps(meta, indent=1))
    print("\nSummary:")
    print(f"  nursing homes : {nh['mapped']}/{nh['source']}  precision {nh['precision']}")
    print(f"  fci centres   : {fci['mapped']}/{fci['source']}  precision {fci['precision']}")
    print(f"  agencies      : {ag['mapped']}/{ag['distinct']} distinct  precision {ag['precision']}")


if __name__ == "__main__":
    main()
