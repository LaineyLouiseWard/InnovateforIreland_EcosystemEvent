# Carer At-Risk Map — workshop build brief

**Goal:** an 8-region (NUTS3) choropleth **website** showing where unpaid carers are
most in need *now*, with a **Now / 2042 toggle** for projected demand and a
**scenario slider** (M1 / M2 / M3), and **zoom-in** to small area. Same pattern as
[the-indices-of-ireland](https://github.com/LaineyLouiseWard/the-indices-of-ireland):
keyless open data, pre-baked to a static JSON, drawn with Leaflet, deployed on
GitHub Pages.

| View | What it shows | Built from | Status (verified 2026-06-08) |
|---|---|---|---|
| **Now** | carer rate per region (carers ÷ population) | `SAP2022T12T2NUTS` ÷ `SAP2022T1T1NUTS` | ✅ **ready** — `data/carer_rate_nuts3.csv` + `data/boundaries/nuts3_2016.geojson` |
| **2042 demand** | projected growth in 65+ (care demand) | `PEC26` (see [MODELLING.md](docs/MODELLING.md)) | ✅ verified live (NUTS3; years 2022–2042; M1/M2/M3); pull pending |
| **At-risk** *(stretch)* | carer rate × deprivation, or demand ÷ carers (strain) | carer rate + Pobal HP | ⚠️ deprivation is **ED-only**; *older/lone-carer* direct measures are **national-only**, not mappable |
| **Zoom-in** *(stretch)* | carer rate **× isolation** by small area | `SAP2022T12T2SA` (+ **no-car** as isolation amplifier; one-person-hh as a lone-recipient/demand signal) | ✅ **ready** — `data/carer_at_risk_small_area.csv` (18,919 SAs) |

**The golden rule:** *pre-bake all data before the session.* The build time goes on
the map + toggle + slider against a ready `regions.json`, not on fetching or parsing.
**The verified data manifest — what's pulled, where it lives, and which layer maps at
which geography — is [SOURCES.md](SOURCES.md).** The Now base layer is already baked
(run `python3 scripts/fetch_carer_data.py` to refresh).

---

## Phase A — Pre-bake (the data chat, beforehand)

Produce two files in `site/` (served statically, no fetch/CORS in the browser):

**1. `site/regions.geojson`** — the 8 **current** NUTS3 polygons (2016/2021, *not* the
2015 set). Each feature needs `properties.region` matching the CSO names: Border,
West, Mid-West, South-East, South-West, Dublin, Mid-East, **Midlands** (plural — this
is what the CSO carer table *and* the GeoHive boundary both use; "Midland" will fail
the join). The ready `data/boundaries/nuts3_2016.geojson` already carries these names
in `NUTS3NAME`; simplify (~10%, mapshaper) to keep it light.

**2. `site/regions.json`** — one row per region, every field filled:

```json
[
  {
    "region": "West",
    "carers2022": 45000,
    "population2022": 460000,
    "carerRate": 9.8,                       // carers per 100 people
    "pop65_2022": 80000,
    "pop65_2042": { "M1": 130000, "M2": 120000, "M3": 110000 },
    "demandGrowthPct": { "M1": 62, "M2": 50, "M3": 38 },   // % change in 65+, 2022->2042
    "oldDependency2022": 23.0,
    "oldDependency2042": { "M1": 0, "M2": 0, "M3": 0 },
    "rankNow": 1                            // 1 = highest carer rate of the 8
  }
]
```

*Optional for an animated year slider:* `pop65ByYear: {"M2": {"2022": …, "2023": …}}`
straight from `PEC26` (annual). The projected fields follow [MODELLING.md](docs/MODELLING.md).

**Validate (the silent-failure step):** all 8 regions present; every `region` name
joins to the GeoJSON; spot-check 2–3 values against the CSO table; national carer
rate lands near 6%.

---

## Phase B — Build (group + Claude Code)

1. **Scaffold + base map.** Static site + Leaflet; load `regions.geojson` + `regions.json`,
   join by `region`, draw the 8 regions, colour by `carerRate`. Log any failed join.
   *(MVP checkpoint — ship this first.)*
2. **Now / 2042 toggle.** Two buttons: **Now** (`carerRate`) and **2042 demand**
   (`demandGrowthPct`). Switch the active field and recolour.
3. **Scenario slider (the star).** M1 / M2 / M3, default **M2** → recompute the 2042
   fields and recolour live. This is the "real-time adjustment" from the brainstorm.
4. **Click-for-detail.** Click a region → popup: carers, carer rate, 65+ now and 2042,
   % growth under the chosen scenario, rank out of 8.
5. **Zoom-in.** *(Stretch)* at high zoom, swap to the small-area layer.
6. **Polish.** Per-view title, sequential **Viridis** colour scale (design team's pick —
   perceptually uniform and colourblind-safe) but **reversed**: yellow = low, purple = high
   ("data heavy"). **Legend on the left** of the map, with a **pinned domain** (so it doesn't
   rescale as the scenario changes). Keep the legend clear that colour means a *rate*, not a
   headcount. CSO attribution, the honesty note.
7. **Deploy.** GitHub Pages: copy the-indices-of-ireland's
   [`.github/workflows/deploy.yml`](https://github.com/LaineyLouiseWard/the-indices-of-ireland)
   (serves the `site/` folder).

**Scope discipline:** get the **Now** map working end-to-end first, then the toggle,
then the slider, then zoom, then polish. One thing working beats four half-built.

---

## Prompts to hand the group (Claude Code)

1. *"Create a static Leaflet website. Load `regions.geojson` (8 Irish NUTS3 regions) and
   `regions.json`, join by the `region` field, draw a choropleth coloured by `carerRate`,
   and log any region that fails to join."*
2. *"Add a Now / 2042 toggle: 'Now' colours by `carerRate`, '2042 demand' colours by
   `demandGrowthPct` for the active scenario. Recolour on switch, keep the colour-scale
   domain pinned per view."*
3. *"Add a scenario slider with three stops M1 / M2 / M3 (default M2). It selects which
   key inside `demandGrowthPct` / `pop65_2042` is used and recolours live."*
4. *"On region click, show a popup: carers, carer rate, 65+ now and projected 2042 under
   the chosen scenario, % growth, and rank out of 8."*
5. *"Add a legend, a per-view title, a 'projections, not predictions' note, CSO
   attribution, and deploy to GitHub Pages serving the `site/` folder."*

---

## Honesty (put it on the map)

- **Projections, not predictions** — the 2042 view is a scenario (M1/M2/M3), not a forecast.
- **Now is measured; future is modelled** — keep the two visually distinct.
- **Small-area future is downscaled** — each area ages like its region (if zoom-in is built).
- **Deprivation/isolation are held at today's values** — they aren't projected.

## Guardrails

- **Pre-bake done** before the session; no live data engineering in the room.
- **Region-name join** is the #1 silent failure — verify all 8 light up in every view.
- **Pin the colour-scale domain** so the map doesn't rescale oddly as the scenario moves.
- All data keys to the same 8 region names.

## Data quick-ref

- **Verified status + produced files:** **[SOURCES.md](SOURCES.md)** — the single source of truth for what's pulled, where it lives, the join keys, and which layer maps at which geography.
- **Boundary:** current NUTS3 (2016) GeoJSON — **already in `data/boundaries/nuts3_2016.geojson`** (GeoHive, 8 features, join on `NUTS3NAME`). SA 2022 boundary verified, pull pending (paginated, heavy).
- **Now:** `SAP2022T12T2NUTS` ÷ `SAP2022T1T1NUTS` (carer rate) — done. Small area + isolation: `data/carer_at_risk_small_area.csv`.
- **Future:** `PEC26` verified (population × age × region × year × M1/M2/M3 → sum single-year ages for 65+; **use M2** as default). `PEC28` (dependency) referenced, dims not yet verified.
- **Geography limits (don't fake precision):** deprivation = **ED only**; 43+ hours burden = **county only** (`F4015`); projections = **NUTS3 only**; older/lone carers (direct) = **national only**. See [SOURCES.md](SOURCES.md).
- **Method:** [MODELLING.md](docs/MODELLING.md). **Why each field:** [DATA.md](docs/DATA.md). **Refresh:** `python3 scripts/fetch_carer_data.py`.
- **Attribution:** CSO (CC BY 4.0); deprivation Pobal HP (CC BY 4.0).
- **Deploy:** `.github/workflows/deploy.yml`, `path: site` — same as the-indices-of-ireland.
