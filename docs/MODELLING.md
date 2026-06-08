# Modelling — projecting carer need forward

How we combine the current carer map (Census 2022, small area / region) with the
CSO regional population projections (`PEC26` / `PEC28`, to 2042) to project carer
need forward. Companion to [DATA.md](DATA.md) (what data) and
[BRAINSTORM.md](BRAINSTORM.md) (the idea). Table codes are in
[DOWNLOAD_MANIFEST.md](DOWNLOAD_MANIFEST.md).

## The core mechanic: age the current map forward

We don't replace the rich 2022 carer map with the coarse 8-region projection. We
**multiply one by the other.**

`PEC26` gives projected population by region × single-year age × year × scenario.
From it we compute a **growth factor** for each region `r`, age band `a`, year `t`:

```
g(r, a, t) = PEC26(r, a, t) / PEC26(r, a, 2022)
```

e.g. "the West's 65+ population is ×1.5 by 2042 under scenario M2." We then apply
these factors to the detailed current data.

- The **spatial pattern** comes from Census 2022 (small-area detail).
- The **time evolution** comes from the projection (regional).

Each half is transparent, and they multiply cleanly. This is the bridge between
the 8-region projection and the ~18,000 small areas of the present.

## What we project — three quantities

Increasing in ambition and in assumptions. They form one pipeline; build outward.

### 1. Care *demand* — cleanest, build first

The population that *needs* care, projected forward:

```
Demand(r, t) = Σ over old ages of PEC26(r, a, t)        # e.g. 65+, or split 65–79 / 80+
```

(80+ need far more care than 65–79, so a split or age-weighting is better than a
flat 65+.) Or use `PEC28`'s projected **old-age dependency ratio** directly as a
one-number "ageing pressure" indicator. Minimal assumptions: pure demography.
Answers *"where does the need grow?"* This is already a legitimate carer
projection, and it needs only `PEC26` plus the current map.

### 2. Carer *supply* — needs the carer-by-age table

Compute current **carer rates by age** from Census 2022 (carers ÷ population per
age band; peaks at 40–64), then apply those fixed rates to the projected age
structure:

```
carerRate(a)  = carers(a, 2022) / pop(a, 2022)
Carers(r, t)  = Σ over a of  carerRate(a) × PEC26(r, a, t)
```

The revealing bit: as the population ages, the 40–64 caring pool flattens while
the 65+ need surges. Requires the `F40xx` carer-by-age table (flagged in the
manifest). Assumption: caring behaviour by age stays constant.

### 3. Carer *at-risk* — the gap between demand and supply (headline)

```
Strain(r, t) = Demand(r, t) / Carers(r, t)             # index to 2022 = 100
```

Where the ratio climbs fastest is where each carer gets stretched thinnest. This
is the **at-risk projection** and the part that lands for a support service.

## Staging: "at-risk projection" or "just carer projection"?

Don't choose. It is one pipeline, each step the previous plus one more input, so
you can stop wherever the build-day clock runs out:

1. **Demand projection** (#1) — a carer projection on its own; extends layer 1 directly.
2. **+ Supply** (#2) → **strain ratio** (#3) — the at-risk projection.
3. **× today's vulnerability** (deprivation, isolation) — "tomorrow's demographic
   pressure meeting today's disadvantage."

## Keeping the zoom-in honest: spatial downscaling

The projection is only 8 regions, but we want small-area detail in the future
view too. Use **constant-share downscaling**: a small area's future value = its
current value × its region's growth factor.

```
Quantity(small_area s, t) = Quantity(s, 2022) × [ Quantity(region r, t) / Quantity(r, 2022) ]
```

Stated plainly: *"each area ages like its region."* It is an assumption (it misses
local new-builds and migration), but it is defensible and labelled, and it lets
the zoom work for the future map, not only the present one.

## A concrete feel for it

> The West already has a high carer load. By 2042 its 65+ population grows ~50%
> (M2), but its 40–64 caring pool is roughly flat, so demand-per-carer rises
> sharply. The region goes dark red on the at-risk projection even though its
> *today* map is only moderate.

That contrast (moderate now, severe by 2042) is the pitch.

## The scenario toggle is the "what-if" layer for free

`PEC26` / `PEC28` come in three migration scenarios:

- **M1** high migration, **M2** moderate (use as central case), **M3** low.

Showing M2 by default and letting the user flip to M1/M3 *is* the "real-time
adjustment to test outcomes" from the original brainstorm. Layer 3 falls out of
the projection method.

## Assumptions and honesty (put these on the map)

- **Projections, not predictions.** Outputs are scenarios under stated assumptions.
- **Constant rates.** Care-need and caring rates by age are held at 2022 levels;
  policy, female employment and health trends will shift them.
- **Vulnerability is held at today's values.** Deprivation and service access are
  not projected, so the at-risk view is future demography on today's disadvantage.
- **Small-area future is downscaled, not independently projected** (constant share).
- **Scenario dependence.** Always state which migration scenario a map shows.

## Data inputs

| Role | Source | Status |
|---|---|---|
| Projected population, region × age × year × scenario | `PEC26` | verified |
| Projected old-age dependency ratio, region | `PEC28` | verified |
| Current carers, region / small area | `SAP2022T12T2NUTS` / `SAP2022T12T2SA` | verified |
| Current population by age, region / small area | `SAP2022T1T1NUTS` / `SAP2022T1T1SA` | NUTS verified; SA to confirm |
| Carers by age (for supply projection) | `F40xx` age table | to locate |
| Deprivation, isolation (vulnerability) | Pobal HP index; Family Carers Ireland centres | external |
