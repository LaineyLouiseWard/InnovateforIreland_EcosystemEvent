# Brainstorm — Carer at-risk map

## The idea

**How might we** help a carer-support service see where unpaid carers are most **at risk of burnout** across Ireland — and where that need will **grow** as the population ages — so support reaches them before crisis?

## Decisions so far

- **For whom:** a carer-support service (their operational view of where need concentrates).
- **Where:** Ireland, national.
- **Map:** Option A — 8 NUTS3 regions, with **zoom-in** to finer geography (small area).
- **Building now:** layer 1 — the current map of where carers are most in need / at risk.

## What the map is

**In one line:** a single-measure map of carer need that you move through *time*, *scenario* and *zoom*. It is not a stack of combined indices.

**One variable on the map at a time,** set by which view you are in:

- **Now view:** carer rate (carers ÷ population, Census 2022).
- **2042 view:** projected care demand — each region's 65+ population grown forward with the CSO projections (`PEC26`), shown as the **% rise in 65+ since 2022**, under the chosen scenario.

**What moves (the axes):**

- **Time:** Now ↔ 2042. The measure *swaps*; the future is not a second layer stacked on the present.
- **Scenario:** M1 / M2 / M3 (migration high / medium / low), 2042 view only.
- **Zoom:** national (8 NUTS3 regions) ↔ regional (small area).

So the dimensions are *time and geography*, not two indicators combined. That is what sets it apart from the-indices-of-ireland (weighted indices with sliders, but frozen in time): here the novel axis is **time**.

**How the 2042 view is produced** ("age the current map forward"): take each region's 2022 older population, apply `PEC26`'s projected growth factor for that region and scenario, and colour by the change. Still one measure on a choropleth, just a different measure than Now. Full method in [MODELLING.md](../_archive/MODELLING.md).

**What the 2042 view is and isn't:** it shows where *demand* grows (more older people needing care), not where *carers themselves* are most stretched. Carer rate alone is not truly "at-risk," and the national rate is nearly flat (5.2–6.3% across the 8 regions), so a deeper "at-risk" reading needs a second variable:

**Optional "at-risk lens" (bivariate, where the data allows):** combine carer *load* with one *vulnerability* measure, highlighting areas worst on both, with no invented weights:

- **carer rate × access/isolation** (no-car households; distance to nearest support service): small-area ✓
- **carer rate × deprivation** (Pobal): Electoral Division only
- older / lone-carer measures: national only, not mappable below the State

(One-person-household %, though available at small-area, is a poor proxy for *carer* isolation — a co-resident carer is not a lone household — so it is read here as a lone care-recipient / demand signal, not used as the isolation amplifier.)

A weighted composite "at-risk score" (sliders, indices-of-ireland style) is possible but imports a weight-choosing problem, so it stays optional.

**In short:** spine = one measure over time (Now = carer rate, 2042 = projected demand; national → regional; scenarios M1–M3), plus an optional bivariate at-risk lens at small-area. See [BUILD_BRIEF.md](../BUILD_BRIEF.md), [MODELLING.md](../_archive/MODELLING.md), [EXTENSIONS.md](EXTENSIONS.md).

## What "at-risk" means here

We can't see individual carers in open data, so we map **area-level concentration** of what drives burnout risk:

- heavy care load — carer rate; hours 43+/week,
- vulnerable carers — older (65+), lone, in deprived/isolated areas,
- rising demand — ageing population.

## What we can plot

Full inventory in [DATA.md](DATA.md). In short — all keyless via CSO PxStat: carer counts/rate (NUTS3 → small area, **confirmed live**), care intensity (hours), older/lone carers, plus context layers (deprivation, 65+ now and projected, isolation/access).

## Build layers

1. **Now** — current carer need (carer rate by NUTS3, zoomable). ← *building*
2. **Future** — projected demand from ageing (Regional Projections 2023–2042, NUTS3). Method in [MODELLING.md](../_archive/MODELLING.md).
3. **What-if** — adjustable inputs to test outcomes (the M1/M2/M3 scenario toggle; see [MODELLING.md](../_archive/MODELLING.md)).

---

## Raw notes

> Draw data into the CSO to see how polci chnages could change the statistics.
>
> Real-time adjustments, to test outcomes?
>
> Forecasting demand for services for carers? as a test-bed.
> Aging population - increased demand over time.
> Need to predict where we will need services.
>
> Use data on population growth? Need now vs need in future?
>
> Potential product to sell to support service companies to support users?
>
> Something to show current need and future need, based on those socioeconomic variables.
>
> Focus on getting the current map of where carers are most 'in need'/at risk.
