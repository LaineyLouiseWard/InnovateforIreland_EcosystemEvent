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
| `boundaries/iha_2025.geojson` | 20 HSE Integrated Healthcare Area polygons (+ health region) | IHA (20) | GeoHive "HSE Integrated Healthcare Areas (2025) generalised 20m", CC-BY-4.0 (`scripts/fetch_iha_boundaries.py`, accessed 2026-06-08) | `IHA_code`, `IHA_operational_name` |
| `sa_to_iha.csv` | Small Area → IHA membership (18,919 rows, 0 unassigned) | SA → IHA | spatial join of SA representative point within IHA polygon (`scripts/build_sa_iha_crosswalk.py`) | `sa_2022_code` → `IHA_code` |

Region names match between the NUTS3 CSV and the boundary file, so the **8-region base map joins directly** — this is the "build first" layer.

The 20 IHAs are the HSE home-support service areas (one approved-provider PDF each) and the geography for Plan 4 (Market Gap). The SA boundary layer carries no IHA field, so `sa_to_iha.csv` is built by spatial join; both layers share CSO Small Areas 2022 lineage, so SAs nest cleanly. Several counties split across IHAs (Dublin → 5, Wicklow/Tipperary/Limerick → 2 each), so a county-dissolve cannot reproduce these boundaries — use the GeoHive polygons.

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

## 3a. Plan 1 — Vulnerability Index (built 2026-06-08)

A 4-theme composite per Small Area, each input percentile-ranked across all 18,919
SAs (0–100, 100 = greatest need), themes averaged. Method: CDC/ATSDR Social
Vulnerability Index + OECD Composite Indicators Handbook. See `_archive/BUILD_PLANS.md`
(Plan 1) and `_archive/VARIABLE_VERIFICATION_REPORT.md`.

| Theme | Input | Source | New file |
|---|---|---|---|
| Care load | carer rate | `carer_at_risk_small_area.csv` (existing) | — |
| Strain | Pobal ED deprivation `Index22_ED_std_rel_wt` | Pobal HP 2022 + SA→ED crosswalk | `pobal_ed_deprivation.csv` |
| Demand | disability rate + % 65+ | `SAP2022T12T1SA`, `SAP2022T1T1SA` | `sa_demographics.csv` |
| Isolation | no-car households | `carer_at_risk_small_area.csv` (existing) | — |

Pipeline (run in order, from `scripts/`): `fetch_demographics.py` → `fetch_deprivation.py`
→ `build_vulnerability_index.py`. The build writes `data/sa_vulnerability.csv`, re-bakes
`site/sa/*.geojson` (props `v cl st dm is` + raw context), rewrites `site/sa/_meta.json`,
and patches `site/regions.json` with per-region theme means for the national view.

Coverage after build: Strain 100%, Demand 100%, Isolation 18,916/18,919 (3 SAs have no
car-household data), Vulnerability 100%. Unmatched boundary polygons: 0.

**Two join gotchas (fixed, worth knowing):**
- **ED key leading zeros** — Pobal drops leading zeros on ~1,400 EDs (`17001`) where the
  ArcGIS boundary keeps them (`017001`). `norm_ed()` (`.lstrip("0")` both sides) makes the
  join exact (3,417/3,417 EDs). Without it only 65% of SAs matched a deprivation score.
- **SA code zero-padding differs per CSO table** — the carer table emits 8-digit codes
  (`17001001`); the age/disability/boundary files emit 9-digit (`017001001`). The existing
  `canon()` helper (pad each numeric part to 9) reconciles all four sources.

The 43+hrs caring variable was dropped — it does not exist at SA level in SAPS.

**ROI only.** All inputs are Republic of Ireland (CSO Census 2022, Pobal, Tailte Éireann
boundaries). Northern Ireland uses separate NISRA geography + the NIMDM deprivation index;
an all-island version would be a distinct join.

---

## 3b. Plan 2 — Care-supply overlay (built 2026-06-08)

Three keyless point layers showing where carer/older-person support physically exists,
toggled on top of the Plan 1 choropleth. A dark (high-need) area with no nearby dots is
a visible gap — usable before the Plan 3 Service-Desert score exists. Built by
`scripts/fetch_supply.py`.

| Layer | Source | Output | Points |
|---|---|---|---|
| Nursing homes | HIQA Register of Designated Centres for Older People (live CSV) | `data/nursing_homes.geojson` | 543 centres |
| Home care agencies | 20 HSE Approved Home-Support Provider PDFs | `data/homecare_agencies.geojson` | 504 rows → 206 distinct offices |
| FCI centres | Family Carers Ireland (curated `data/fci_centres.json`) | `data/fci_centres.geojson` | 16 addressed centres |

Sources (keyless, accessed 2026-06-08):
- HIQA CSV: `https://www.hiqa.ie/centre/export/older_persons_register.csv?_format=csv`
  — live-generated, 20 cols; name `Centre_Title`, full address (Eircode inline)
  `Centre_Address`, `County`, `Maximum_Occupancy` (beds), `Centre_Phone`.
- HSE index: `https://www2.hse.ie/services/home-support-service/choosing-an-approved-provider/`
  — 20 region PDFs, Word-generated (text-extractable). Parsed with PyMuPDF: each table
  row reconstructed by bucketing words to the nearest website-token anchor, then split
  into columns by the header x-positions. 93% of distinct offices carry an Eircode.
- FCI: `https://www.familycarers.ie/carer-supports/get-support/` — 28 county listings →
  ~17 distinct offices; 15 have a full address + Eircode (Waterford town-only; Louth/Meath
  publish no address → omitted, logged).

**Geocoding.** Eircodes are *not* openly geocodable (ECAD is licensed), so each address is
resolved with OSM Nominatim (keyless, 1 req/s, descriptive User-Agent) with progressive
fallback: full address → town+county → county. Results cache to `data/raw/geocode_cache.json`
so the slow pass runs once; `supply_meta.json` records the precision mix (address vs town
vs county) per layer. Points geocoded to town/county are flagged "approx" in the tooltip.

Served copies are mirrored to `site/supply/*.geojson`; `site/zoom.html` gains a "Care
supply" panel with three toggles (default off), distinct coloured markers, and click
tooltips (name, beds/serves, address, phone, website). **ROI only** — NI nursing homes
(RQIA) and home-care providers are a separate registry.

---

## 3c. Plan 4 — Market Gap Score (IHA level, built 2026-06-08)

The operator/investor view: aggregates Plan 1 demand and Plan 2 supply to the **20 HSE
Integrated Healthcare Areas** (the geography a home-support provider applies to serve).
Built by `scripts/build_market_gap.py`.

| Step | Method | Output |
|---|---|---|
| Demand per IHA | population-weighted mean of Plan 1 `vulnerability_score`, rolled up via `sa_to_iha.csv` | `mean_vulnerability` |
| Supply per IHA | distinct approved providers, counted straight from the 20 HSE PDFs (`data/raw/iha/*.pdf`, filename→IHA) — no geocoding needed | `provider_count` |
| Density | providers per 1,000 people aged 65+ (`sa_demographics.pop_65plus`) | `providers_per_1k_65plus` |
| Score | `PR(mean vulnerability) / PR(provider density)`, percentile-ranked across the 20 IHAs | `market_gap_score` |

Outputs: `data/iha_market_gap.csv` (ranked, the operator export), `site/iha/iha_market_gap.geojson`
+ `site/iha/_meta.json`. The site gains a third tab, **Market Gap** — IHA choropleth, ranked
list, click-to-zoom, and a client-side CSV download. No Fair Deal adjustment in v1.

Sanity checks: population 5,148,496 and 65+ 776,149 reconcile with Census 2022 ROI totals;
all 20 IHAs have providers; per-IHA provider sum 493 (national distinct 206 — multi-area
providers counted in each area they serve, which is correct for "competition here").

**Score-scale caveat.** The normalised ratio is a *ranking* tool, not a linear magnitude:
dividing two percentile ranks inflates the score when the denominator IHA is the single
lowest-density one (Kerry = 33 vs next 3.4). The **ranking is sound** (Kerry: lowest density +
high need = #1 gap); lead with rank in any narrative. The choropleth uses quantile classes,
so it is outlier-robust. A bounded form (`PR_vuln × (1 − PR_dens/100)`) is the drop-in
alternative if comparable magnitudes are ever needed.

**Provider count is by PDF, not point-in-polygon.** The 20 PDFs *are* the IHA partition, so
counting per PDF is exact and needs no coordinates — it sidesteps the Plan 2 geocoding
precision caveat entirely for Plan 4. (Point-in-polygon on town/county-geocoded offices
would have been noisier.)

---

## 3d. Town names — SA → human place (built 2026-06-08)

So the capstone drill-down reads "near Listowel, Co. Kerry" instead of "SA 077128019".
Built by `scripts/build_town_names.py`; output `data/sa_town_names.csv`
(`sa_2022_code, town_name, town_name_alt, county, method, distance_km`).

Single keyless source — the **CSO/Tailte Small Area 2022 layer already tags each SA**
with the named CSO Settlement it sits inside (`SA_URBAN_AREA_NAME`) and its county
(`COUNTY_ENGLISH`). Attribute table only, no geometry, same FeatureServer as the SA
boundaries; pull cached to the gitignored `data/raw/sa_attributes.json`.

| Case | Rule | `method` | `distance_km` |
|---|---|---|---|
| Inside a settlement (13,185 SAs) | use that settlement's name | `within_settlement` | SA → settlement-centre |
| Rural (5,734 SAs) | nearest of the 848 settlement centroids **in the same (traditional) county**, vectorised Haversine | `nearest_settlement` | SA → that centre |

Settlement centroids are derived in-script (mean of each settlement's member-SA centroids)
— no extra download, no API key. All 18,919 SAs named; the ~200 capstone targets all resolve
(0 awaiting). `build_target_drilldown.py` joins it on `sa_2022_code`, falling back to the raw
code if absent, and carries `town_alt` + `town_km` into the drill-down JSON.

**Same-county constraint.** Straight-line nearest otherwise crosses water: a Loop Head SA
(Clare) is 13 km from Ballybunion as the crow flies but a ~100 km drive around the Shannon
estuary — and Ballybunion is in *Kerry*, so "Ballybunion, Clare" was both a wrong county and
unreachable. Restricting to the SA's own county (city/county splits merged to the traditional
county) reassigns it to Kilkee, Clare. Mild overall effect (median rural match 3.8→3.9 km,
nothing orphaned); it also matches the IHA/county an operator actually works in.

**Bilingual names.** Gaeltacht settlements are stored under their official CSO **Irish** name
with `town_name_alt` giving the common English form, so a search for "Belmullet" still finds
Béal An Mhuirthead (283 SAs across 25 settlements; e.g. Ailt An Chorráin → Burtonport, Gob an
Choire → Achill Sound). Every alias verified on [logainm.ie](https://www.logainm.ie), the
official Placenames Database of Ireland.

**Honesty.** `town_name` is the *nearest settlement*, not an exact address — `distance_km`
keeps far matches auditable. 15 targets sit >10 km from their nearest same-county town (worst:
Oughterard 21 km) — genuinely remote peninsulas (Erris, Connemara, Mizen, Beara) that are the
real service deserts. The UI uses `town_km` to say "nearest town: X (N km)" when far rather
than implying "near".

---

## 4. Caveats

- **Area rates, not individuals** — we map where risk factors co-occur by area; open data can't identify which carers are themselves poor/unwell.
- **One-person-household % is a demand signal** (lone care-recipient), not a carer-isolation proxy — a co-resident carer isn't a lone household. Use **no-car households** (+ distance-to-service) as the small-area isolation amplifier.
- **Avoid the "+50% since 2016"** carer-growth headline — the census question wording changed.
- **NUTS3 name**: CSO uses "Midlands" here; both the CSV and the boundary use it, so the join is clean — but watch this if swapping in a Eurostat boundary (which uses "Midland").
- **Projections** are scenario-dependent and region-level only — any future layer must state the scenario (M2) and that it's coarser than the "now" view.
