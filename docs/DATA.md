# Data inventory — what we can plot for "carers at-risk"

All CSO data is **keyless and open** via the PxStat API (JSON-stat/CSV). Census 2022 carer data is published at many geographies, so we can map national → zoom to small area. Verified live against the API on 2026-06-08.

## The question we're representing

*Where are unpaid carers most at risk of burnout?* We can't see individual carers in open data, so we map **area-level concentration** of the things that drive risk. "At-risk" = heavy care load **and** a vulnerable carer (older, lone, in a deprived/isolated area) **and** rising demand.

## Core carer measures — confirmed, 2022

| Plot | What it shows | CSO table | Geography |
|---|---|---|---|
| Carer count | how many carers | `SAP2022T12T2NUTS` | NUTS3 (8) |
| **Carer rate** (carers ÷ pop) | where caring is common | `SAP2022T12T2NUTS` ÷ `SAP2022T1T1NUTS` | NUTS3 |
| Carer % of population | same, ready-made + time series | `FY088` | County & City (2011/16/22) |
| Carers by county | county detail | `F3064`, `F4015`, `F4068` | County & City (31) |
| Carers by small area | **the zoom-in layer** | `SAP2022T12T2SA` | Small Area (~18k) |
| Carers by HSE network | service-aligned view | `DHGA09CHN` / `CST` / `HR` | HSE CHN (97) / CST (30) / Region |

## Risk dimensions — make caring hard (confirm exact table/geography when wiring up)

- **Care intensity** — hours of unpaid help/week; **43+ hrs = heavy burden** (29% of carers nationally). Lives in the Census 2022 carer theme (`F40xx`); confirm which table carries hours by region/small area.
- **Older carers (65+)** — caring at an age you may need care yourself. Carer age breakdowns available in the `F40xx` series.
- **Lone carers** — carers living alone / one-person households.

## Context amplifiers — area-level, raise the risk

- **Deprivation** — Pobal HP Deprivation Index (small area, standardised score). External to CSO but keyless. Proxy for "can't afford private respite."
- **Ageing / future demand** — population 65+ now (SAP2022 age tables: NUTS3 / county / small area) **and** [Regional Population Projections 2023–2042](https://www.cso.ie/en/releasesandpublications/ep/p-rpp/regionalpopulationprojections2023-2042/) for *where demand grows*: `PEC26` (projected population, single-year age × NUTS3 × year 2022–2042 × scenario M1/M2/M3 — derive 65+/85+) and `PEC28` (projected old-age dependency ratio × NUTS3). See [DOWNLOAD_MANIFEST.md](../_archive/DOWNLOAD_MANIFEST.md).
- **Isolation / access** — distance to the 22 Family Carers Ireland centres; low car availability (census SAPS).

## Geographies available for carers (2022)

NUTS3 region (8) · County & City (31) · Local Electoral Area · Electoral Division · Small Area (~18k) · HSE Community Health Network / Specialist Team / Health Region · Province.

## Access

PxStat JSON-stat: `https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/<CODE>/JSON-stat/2.0/en` — no key, no login.
Boundaries: use the **current** NUTS3 (2016/2021, e.g. Eurostat GISCO or Tailte Éireann) — **not** the 2015 set (Louth and Tipperary moved regions).

## Caveats

- **Area rates, not individuals** — we can't identify carers who are *themselves* poor/unwell without microdata; we map co-occurrence by area.
- **Projections are NUTS3 only** — no off-the-shelf small-area future; the future layer sits at region level, or is derived with a stated assumption.
- Don't lean on the 2016→2022 "+50%" growth figure (the carer question wording changed).
