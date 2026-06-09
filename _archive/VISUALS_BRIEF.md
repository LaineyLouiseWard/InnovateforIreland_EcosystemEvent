# Brief for the visuals chat — carer need/supply map

Hand this whole file to a new Claude Code chat. It is the visual-design pass over a
working data pipeline. **The data and methods are done and correct — do not change them.**
Your job is presentation only: layout, colour, hierarchy, interaction, copy.

## Role
You are a frontend/data-viz designer polishing a working prototype (Leaflet + vanilla JS,
no build step). Make it clear, credible and presentable for a non-specialist audience
(carers, planners, care operators). Keep it a static site (`site/`), no frameworks.

## Read first (in this order)
1. `README.md`, `CLAUDE.md` — what the project is and the working conventions.
2. `_archive/HANDOFF_PLAN1-2_TO_3-4.md` — how demand (areas) and supply (points) fit together.
3. `SOURCES.md` §3a/§3b — the data and its caveats.
4. The live pages: `site/index.html` (homepage: Home / Heatmap / Market Gap tabs) and
   `site/zoom.html` (the full measure map). Serve with `python3 -m http.server` in `site/`.

## The data you're visualising (already built — read, don't rebuild)
Per **Small Area** (18,919 areas), in `site/sa/<region>.geojson` properties:
- `v` Vulnerability (headline), `cl` Care load, `st` Strain, `dm` Demand, `is` Isolation,
  `sd` Service desert — all **percentile ranks 0–100** (100 = greatest need).
- `dn` km to nearest carer support, `nsup` count of carer-support services within
  `_meta.density_km` (25) km, `nt`/`nl` nearest type + geocode precision.
- `cr` carer rate %, `a65` % 65+, `dr` disability % (raw context).
- `site/sa/_meta.json` has `measures` (labels), `breaks` (quantile classes per measure),
  `density_km`, and `regions` (per-region file index).
- `site/regions.json` has per-region **means** (`vMean`, `clMean`, … `sdMean`) for the
  national view, plus the old `carerRate`/`noCarPct`/`lonePct`.
- `site/supply/*.geojson` — nursing homes / home-care agencies / FCI points (toggle layers).
- `site/iha/iha_market_gap.geojson` + `site/iha/_meta.json` — 20 HSE-area Market Gap polygons.

## Tasks (presentation only)
1. **Vulnerability-first layout.** Make **Vulnerability** the headline view — the heatmap
   you land on. Move the other five measures (Care load, Strain, Demand, Isolation, Service
   desert) into a **dropdown or side menu**, not a row of equal tabs. Vulnerability is the
   answer; the five are the "why" behind it.
2. **Fix the two-level colour mismatch.** The national/region view currently colours the 8
   regions by their *mean* using the *small-area* breaks, so regions look washed-out
   mid-tones (means bunch ~40–60; small-area values span 2–98). Give the **region view its
   own colour breaks** (quantiles of the 8 region means), and add a one-line note that
   region colour = average, small-area colour = the area's own value. (See "the trap" below.)
3. **Integrate the three views into one coherent story**, ideally one map with levels:
   - National (8 regions) → click → Small Areas (the zoom-in breakdown) for the 6 measures.
   - The **Market Gap (20 HSE areas)** view (`site/iha/`) as a third level/tab — it's the
     operator-facing ranking. Tie it in, don't leave it as an orphan tab.
4. **Service-desert storytelling.** The Service desert measure has a "greatest unmet need"
   table + top-100 highlight already in `zoom.html`. Make it legible and obvious.
5. **Supply dots.** Keep the three toggle layers; make the legend/markers clear. Nursing
   homes are context only (they don't drive the desert score) — reflect that visually.
6. **Mobile/scaling, copy, accessibility** — your call, to a presentable standard.

## The trap to communicate (don't let it mislead)
Region colour is an **average** and hides internal spread. Example: carer rate is 5.2–6.3%
across the 8 regions (looks flat) but **0–20.5%** across small areas (5th pct 2.3%, median
5.8%, 95th 9.9%). The story is *fine-grained need hidden by coarse averages* — design so a
muted region never reads as "nothing to see here." Lead users to drill in.

## Hard constraints
- **Do not touch** `scripts/*.py` or any `data/*` / `site/**/*.geojson` / `*_meta.json`
  contents — those are the methods pipeline (owned by another chat). You may read them.
- Percentile ranks are 0–100 **scores**, not percentages — don't relabel them "%".
- Keep it **ROI-only** and keep the existing honesty caveats (geocoding precision; office
  ≠ delivery location; area-level not individuals).
- Static site, no build tooling, no API keys.

## Output
Edited `site/*.html` (+ any small `site/` css/js assets). Verify in a headless browser
screenshot before claiming it works. List what you changed and why.

---

## UPDATE (read this — added after the brief was first written)
The methods chat has since finalised more of the product. Bring your build in line with it:

1. **Read `docs/CAPSTONE_CONCEPT.md` and `docs/METHODOLOGY.md`** — the agreed product shape
   and the grounded method. They supersede any conflicting detail above.
2. **The capstone "Target your supply here" view now has data.** `site/iha/target_drilldown.json`
   = the 20 HSE areas ranked by Market Gap, each with its 10 worst service-desert towns
   (`towns[]` with `desert`, `d_nearest_km`, `nearest_type`, `nearest_loc` precision flag,
   `lat`/`lon` for pins). Build the operator answer view from this — a ranked IHA list, each
   expandable to its target towns, with a highlight map. (Town labels currently show as SA
   codes; a separate chat is producing real names into the file — your UI should just render
   `town`, whatever it contains.)
3. **The "opportunity" headline map** = a Need × Supply **bivariate** of the small areas
   (Vulnerability × distance-to-support), reusing the existing Stevens 3×3 engine in
   `index.html`. See `CAPSTONE_CONCEPT.md` §2B. Demote the legacy bivariates to breakdown
   lenses sharing the one need axis.
4. **Make "zoom" vs "switch lens" visually obvious** — a user must instantly understand that
   zooming changes *how local* and the lens changes *what the colour means*. Two distinct,
   clearly-labelled controls; don't let them blur together.
5. **New per-area field:** `nsup` = carer-support services within `_meta.density_km` (25) km —
   already in the SA tooltip; surface it sensibly.

Everything in this UPDATE is still presentation-only — the data and `scripts/` remain off-limits.
