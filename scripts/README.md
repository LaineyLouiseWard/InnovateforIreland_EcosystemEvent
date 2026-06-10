# Data pipeline

How the map's data is fetched and built, end to end. Every source is **open and keyless** —
no API keys, no logins, no paid lookups. The guiding rule is *pre-bake everything*: the scripts
pull and process data offline into the static JSON/GeoJSON the site serves, so the browser never
makes an API call.

Run from the repo root with the conda env active (`environment.yml`). Raw downloads land in the
gitignored `data/raw/`; processed outputs in `data/` and `site/`. Provenance, URLs and join keys
for every dataset are in [`../docs/methods/SOURCES.md`](../docs/methods/SOURCES.md); the scoring
behind each layer is in [`../docs/methods/METHODOLOGY.md`](../docs/methods/METHODOLOGY.md).

## How we access each source (all keyless)

- **CSO Census 2022 (PxStat)** — a public REST endpoint, one URL per table:
  `https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/<CODE>/JSON-stat/2.0/en`.
  No key. Carer counts, population, age, disability, no-car households.
- **Pobal HP Deprivation 2022** — a published CSV (Electoral Division level), joined down to small
  areas via a spatial crosswalk.
- **HIQA nursing-homes register** — a live-generated CSV export.
- **HSE approved home-support providers** — 20 region PDFs, parsed with PyMuPDF (one per HSE area).
- **Boundaries** — CSO/Tailte Éireann Small Areas and GeoHive HSE areas, fetched as GeoJSON from
  their public ArcGIS FeatureServers.
- **Geocoding** — OSM Nominatim (keyless, 1 request/second, descriptive User-Agent). Eircodes are
  not openly geocodable, so addresses resolve to street / town / county and each point carries a
  `loc` precision flag.

## Scripts, in dependency order

**Fetch (source → `data/`):**

| Script | Pulls | Output |
|---|---|---|
| `fetch_carer_data.py` | CSO carers + population (NUTS3 and Small Area) | carer rates |
| `fetch_demographics.py` | CSO % aged 65+ and disability rate | `sa_demographics.csv` |
| `fetch_deprivation.py` | Pobal HP Deprivation (ED → SA crosswalk) | `pobal_ed_deprivation.csv` |
| `fetch_sa_boundaries.py` | CSO Small Area 2022 polygons | per-NUTS3 GeoJSON |
| `fetch_iha_boundaries.py` | GeoHive HSE Integrated Healthcare Areas (20) | `boundaries/iha_2025.geojson` |
| `fetch_supply.py` | HIQA homes, HSE home-care PDFs, FCI centres; geocodes them | supply GeoJSON layers |

**Build (scores and joins):**

| Script | Builds |
|---|---|
| `build_sa_iha_crosswalk.py` | each Small Area → its HSE area (`sa_to_iha.csv`) |
| `build_vulnerability_index.py` | the 4-theme Vulnerability Index per Small Area |
| `build_service_desert.py` | Vulnerability × distance to nearest carer support |
| `build_market_gap.py` | need vs provider density per HSE area (operator view) |
| `build_residential_gap.py` | Demand × distance to nearest nursing home (additive lens) |
| `build_town_names.py` | Small-Area code → nearest settlement name |
| `build_target_drilldown.py` | the capstone "target your supply here" JSON |
| `bake_site_data.py` | the NUTS3 "Now" base layer for the site |
| `check_robustness.py` | theme correlations + composite-vs-flag-count rank agreement (reads `site/sa/`, no fetch needed) |

A typical full rebuild runs the fetch scripts, then the build scripts in the order above. Each is
re-runnable; the slow geocoding pass caches to `data/raw/` so it only happens once.
