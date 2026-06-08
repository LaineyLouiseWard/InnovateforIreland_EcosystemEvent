# Data download manifest

> **Superseded — see [SOURCES.md](../SOURCES.md) for live status.** Layer 1 (current
> carer need) is pulled and baked; layer 2 (projections `PEC26`/`PEC28`), deprivation
> and Family Carers centres are still pending. This file is kept as the original
> scoping brief; `SOURCES.md` is the source of truth for what exists and where.

A self-contained brief for a follow-up chat to fetch the datasets we scoped.
Hand each dataset below to a subagent. All table codes verified live against the
CSO PxStat API on 2026-06-08.

## Read first

- [DATA.md](DATA.md) — why each dataset matters (the "at-risk" framing).
- [CLAUDE.md](../CLAUDE.md) — repo conventions (keyless data, provenance, gitignore).

## Access pattern (keyless)

CSO PxStat, JSON-stat 2.0:

```
https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/<CODE>/JSON-stat/2.0/en
```

No key, no login. JSON-stat is a flat value array indexed by the dimension order
in `dataset.id`; pick the `Both sexes` / `State+regions` slices. CSV/XLSX also
available from each table's page on data.cso.ie if a subagent prefers tabular.

## Datasets to download

### Layer 1 — current carer need (priority)

| # | Purpose | Code | Geography | Key dims |
|---|---|---|---|---|
| 1 | Carers (numerator) | `SAP2022T12T2NUTS` | NUTS3 (8) | Sex |
| 2 | Population (denominator) | `SAP2022T1T1NUTS` | NUTS3 (8) | Sex, Age |
| 3 | Carers, zoom-in | `SAP2022T12T2SA` | Small Area (~18k) | Sex |
| 4 | Population, zoom-in (denominator) | `SAP2022T1T1SA` *(verify code)* | Small Area | Sex, Age |

→ carer rate = carers ÷ population, per area.

### Layer 2 — future demand (ageing)

| # | Purpose | Code | Geography | Key dims |
|---|---|---|---|---|
| 5 | Projected population, single-year age | `PEC26` | NUTS3 (8) | Year 2022–2042 (annual), Age (0–100+), Sex, Scenario M1/M2/M3 |
| 6 | Projected old-age dependency ratio | `PEC28` | NUTS3 (8) | Year (5-yr to 2042), Scenario, Dependents Status (use "Old dependency") |

→ derive 65+ (and 85+) per region per year by summing the relevant single ages
in `PEC26`; use scenario **M2** as the central case.

### Amplifiers / later layers (optional)

| # | Purpose | Source |
|---|---|---|
| 7 | Carers by hours (43+/week) | CSO `F40xx` series — subagent to locate the 2022 table carrying hours by region/small area |
| 8 | Carers by age (older carers) | CSO `F40xx` series — age breakdown |
| 9 | Deprivation | Pobal HP Deprivation Index (pobal.ie) — small area, keyless |
| 10 | Service access | Family Carers Ireland — 22 centre locations (familycarers.ie), geocode |

### Boundaries (for the map)

| # | Purpose | Source |
|---|---|---|
| 11 | NUTS3 regions | **current 2016/2021** GeoJSON (Eurostat GISCO `NUTS_RG_*_2021_4326_LEVL_3`, filter `CNTR_CODE=IE`; or Tailte Éireann). **NOT** the 2015 set — Louth and Tipperary moved regions. Match on region name. |
| 12 | Small Areas 2022 | CSO / Tailte Éireann Small Area 2022 boundaries (for zoom-in). |

## Conventions (from CLAUDE.md)

- Save raw pulls to `data/raw/` (gitignored). Commit only processed outputs.
- Record each source URL + access date in a `SOURCES.md` entry.
- Everything here is keyless — if a source asks for a login/key, it's the wrong source.
- Region names in CSO tables: Border, West, Mid-West, South-East, South-West,
  Dublin, Mid-East, Midland (+ "State"/Ireland total). Normalise "Midland"/"Midlands".

## Expected outputs

1. Tidy CSVs per dataset: columns `geography, year, scenario, sex, value`.
2. Layer 1: `nuts3_carer_rate.csv` and a joined `nuts3_carers.geojson` (carer rate per region).
3. Layer 2: `nuts3_pop65plus_2022_2042.csv` (65+ per region per year, M2) from `PEC26`.
4. A `SOURCES.md` provenance entry for each.
