# Business case — Carer Map Ireland

Why this map could be more than a prototype: the gap it fills, who would pay, and what the
market looks like. Merged from the one-day pitch and the market research compiled 2026-06-08.

> **Status.** This is a one-day AI Build Day prototype, not a commercial service. The operator
> login and the company **MedVizion** are a fictional demo wrapper around the public map; the
> product concept is **Carer Map Ireland**. Nothing here is being sold.

## The gap

Ireland has no integrated demand-and-supply intelligence tool for the care sector. Site-selection
decisions for nursing homes and home-care agencies are made on gut feel, Fair Deal rate schedules,
and reactive CBRE valuations. The UK equivalents — Carterwood Analytics and Oscar Research — are
explicitly GB/UK only. The closest Irish thing, poidata.io, is a points-of-interest directory with
no demand modelling, no gap analysis, and no demographic overlays. A 2021 composite-index study of
Irish nursing-home access had to hand-assemble HIQA, CSO and HSE data because no integrated
location intelligence exists. The pitch, in a line: **Carterwood for Ireland.**

## What it is

An interactive map of where unpaid-carer need is greatest versus where care services exist,
at small-area resolution.

- **Demand:** a small-area Vulnerability Index (carer rate, deprivation, disability, age 65+)
  across all **18,919** CSO small areas.
- **Supply:** **543** nursing homes (HIQA register), **16** Family Carers Ireland centres, and
  **201** home-care offices mapped from the 20 HSE approved-provider lists (206 distinct offices,
  504 raw rows).
- **Derived:** Vulnerability, Service Desert, and Market Gap scores.

## Market

| Segment | Scale |
|---|---|
| Nursing-home sector revenue | ~€800m (~2% CAGR); 543 HIQA-registered homes, 10 funds hold ~1/3 of beds |
| Home-care market | USD 2.9bn (2024) → 5.4bn (2030), ~11% CAGR |
| Nursing-home beds needed by 2040 | 19,500–25,000 (ESRI Hippocrates); only 443 delivered in 2024 |
| Over-65 population by 2051 | 1.6m (doubling); over-80s up 271% |

Home care is being formally regulated for the first time (Health Amendment Bill, Dec 2025),
creating immediate demand for compliance and market-entry intelligence.

## Who pays

| Customer | Pain | Willingness |
|---|---|---|
| Nursing-home developer / investor | Where do I build? Rural Fair Deal rates don't cover costs | **High** — CBRE already charges for reactive valuation |
| Home-care operator expanding | Which IHA do I apply for? High demand, thin competition? | **High** — an operational decision worth real revenue |
| HSE / Family Carers Ireland planner | Where do we direct limited resources? | **Low** — free public tool or grant-funded |

The paying customer is the **operator or investor**; the free public planner view is the
credibility layer that makes the paid product defensible.

## Same map, two front doors

- **Planner framing** ("where is need concentrated?"): high carer rate + deprivation + disability,
  against nearby support. Output: where need is greatest and services furthest away.
- **Site-selection framing** ("where is my market?"): same demand variables, against competitor
  density. Output: high need, low supply, viable Fair Deal catchment.

The data engine is identical; only the UI framing and variable emphasis change. That flip —
"market opportunity ⇄ unmet need" over the same place — is the product's thesis.

## Structural constraints

- **Nursing homes:** HIQA registers per site on quality, with no geographic cap. Fair Deal rates
  (NTPF) vary by county (Dublin €1,335/wk vs Donegal €1,125/wk — a ~€655k/yr gap per 60-bed home),
  leaving rural areas structurally unviable. The North-West (Donegal, Sligo, Leitrim, Roscommon)
  is most underserved relative to need.
- **Home care:** the HSE Authorisation Scheme assigns approved providers to specific IHAs (20 areas
  in 6 health regions). A new entrant nominates which IHA(s) to serve. IHA boundaries are free on
  GeoHive.

## Tech

Leaflet front end; Python pipeline over entirely open, keyless sources (CSO PxStat, HIQA, HSE,
Pobal); deployed on Vercel. No proprietary data required. See [`../../scripts/README.md`](../../scripts/README.md)
for the pipeline and [`../methods/METHODOLOGY.md`](../methods/METHODOLOGY.md) for the scoring.

## Key sources

- [Carterwood Analytics (GB benchmark)](https://www.carterwood.co.uk/analytics-elderly-care-homes/)
- [HIQA nursing-homes register, Jan 2026](https://www.hiqa.ie/sites/default/files/2026-01/List-of-centres-13-January-2026.pdf)
- [ESRI Hippocrates regional projections to 2040](https://www.esri.ie/publications/projections-of-regional-demand-and-bed-capacity-requirements-for-older-peoples-care-in)
- [PMC composite access/need index for Irish nursing homes](https://pmc.ncbi.nlm.nih.gov/articles/PMC8669779)
- [HSE Home Support Authorisation Scheme SOP 2025](https://www.hse.ie/eng/services/list/4/olderpeople/home-support-authorisation-scheme-standard-operating-procedure-2025.pdf)
- [GeoHive: HSE Integrated Healthcare Areas 2025](https://www.geohive.ie/items/7c0665223cda494aa22b5dee643a0ac0)
