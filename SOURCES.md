# Data sources & status — carer at-risk map

Verified live against the source APIs/files on **2026-06-08**. All keyless and open.
Refresh everything with `python3 scripts/fetch_carer_data.py` (raw pulls land in the
gitignored `data/raw/`; processed CSVs in `data/`).

CSO PxStat pattern (no key):
`https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/<CODE>/JSON-stat/2.0/en`

---

## 1. Ready now — in `data/` (build can start)

| File | What | Geography | Built from | Join key |
|---|---|---|---|---|
| `carer_rate_nuts3.csv` | carers, population, **carer_rate_pct** | 8 NUTS3 regions + State | `SAP2022T12T2NUTS` ÷ `SAP2022T1T1NUTS` | `region` (name) |
| `carer_at_risk_small_area.csv` | carer_rate_pct, **no_car_hh_pct** (isolation/access amplifier), **one_person_hh_pct** (lone care-recipient / demand signal) | 18,919 Small Areas | `SAP2022T12T2SA`, `SAP2022T1T1SA`, `SAP2022T5T1SA`, `SAP2022T15T1SA` | `sa_2022_code` |
| `boundaries/nuts3_2016.geojson` | region polygons (WGS84, 8 features) | NUTS3 | GeoHive / Tailte Éireann | `NUTS3NAME` |

Region names match between the NUTS3 CSV and the boundary file, so the **8-region base map joins directly** — this is the "build first" layer.

NUTS3 carer rate (sanity check): State 5.81% (≈299,128 carers ✓), West highest at 6.35%, Dublin lowest at 5.22%.

---

## 2. The geography reality (shapes what we can map)

The at-risk drivers do **not** all live at the same geography. This is the key build constraint:

| Layer | Finest open geography | Choropleth? |
|---|---|---|
| Carer rate | **Small Area** | ✅ SA + NUTS3 (have it) |
| Lone care-recipient — one-person households | **Small Area** | ✅ (have it) — a demand signal, not carer isolation |
| **Isolation/access** — no-car households | **Small Area** | ✅ (have it) — the small-area isolation amplifier |
| Ageing demand — 65+ share *now* | Small Area (derive from `SAP2022T1T1SA` age bands) | ✅ derivable |
| Deprivation — Pobal HP index | **Electoral Division** (open) | ✅ at ED only (SA is licensed) |
| Care intensity — 43+ hrs/week | **County/City** | ⚠️ coarse only |
| Future demand — 65+ projected to 2042 | **NUTS3** | ⚠️ coarse only |
| Older carers / lone carers (direct measure) | **National only** | ❌ not mappable |

**Implication:** the honest Small-Area heatmap = carer rate + isolation (+ derivable 65+-now). Deprivation joins at ED, the 43+ burden at county, and the future-demand story at region — show those as their own layers, not faked down to Small Area.

---

## 3. Verified & ready to pull (not yet downloaded)

Codes/URLs below are all confirmed live; wiring them in is the next step.

**Small Area 2022 boundaries** (the zoom-in geometry)
`https://services-eu1.arcgis.com/BuS9rtTsYEV5C0xh/ArcGIS/rest/services/SMALL_AREA_2022_Genralised_20m_view/FeatureServer/0/query?where=1=1&outFields=SA_PUB2022,SA_NUTS3,SA_NUTS3_NAME&f=geojson`
- 18,919 features, generalised 20m, WGS84. Join key `SA_PUB2022` (bare 9-digit, matches `sa_2022_code`). Also carries `SA_NUTS3` for rollup.
- **Paginated**: `maxRecordCount=2000` → ~10 requests with `resultOffset` (0,2000,…). Tens of MB — consider scoping the demo to one county first.

**Pobal HP Deprivation Index 2022** (ED level, CC-BY)
`https://www.pobal.ie/wp-content/uploads/2024/01/hp-deprivation-index-scores-2022.csv`
- 3,417 EDs. Join key `ED_ID_STR` (6-digit). Score `Index22_ED_std_rel_wt` (neg = deprived); category label `Index22_ED_rel_wt_lab`. SA-level version is licensed — use ED.

**Care intensity — 43+ hours** → table `F4015` (County/City only)
- Hours dim `C02738V03306`, band `43 or more hours unpaid help per week`. State 43+ = 39,982 (all ages). Pair with population for a county "heaviest-burden" rate.

**Future demand — projections** → table `PEC26` (NUTS3)
- Years 2022–2042; age dim `C02076V02508` is single-year (sum `065`…`098` + `646` for 65+); scenario dim `C02466V02984` = M1/M2/M3 (**use M2** as mid-range, label the choice).

**Family Carers Ireland centres** (for distance-to-nearest)
- ~15 verified centre addresses with Eircodes from `familycarers.ie/find-us/get-support` (Louth, Meath, Waterford had no street address). No coordinates published → geocode the addresses with Nominatim (keyless): `https://nominatim.openstreetmap.org/search?q=<addr>&format=json&countrycodes=ie` (1 req/s, set a User-Agent).

---

## 4. Caveats

- **Area rates, not individuals** — we map where risk factors co-occur by area; open data can't identify which carers are themselves poor/unwell.
- **One-person-household % is a demand signal** (lone care-recipient), not a carer-isolation proxy — a co-resident carer isn't a lone household. Use **no-car households** (+ distance-to-service) as the small-area isolation amplifier.
- **Avoid the "+50% since 2016"** carer-growth headline — the census question wording changed.
- **NUTS3 name**: CSO uses "Midlands" here; both the CSV and the boundary use it, so the join is clean — but watch this if swapping in a Eurostat boundary (which uses "Midland").
- **Projections** are scenario-dependent and region-level only — any future layer must state the scenario (M2) and that it's coarser than the "now" view.
