# Capstone concept — "Target your supply here"

Synthesis of three design drafts (operator tool · need×supply bivariate · unified flow).
They are not rivals — they're the **answer**, the **headline map**, and the **skeleton** of
one product. This doc is the agreed concept; the *data* tasks below belong to the methods
chat, the *visual build* to the visuals chat (`docs/VISUALS_BRIEF.md`).

---

## 1. The product in one line
One map, **three zoom levels** — National (8 regions) → **IHA (20 HSE areas)** → Small Area
(18,919) — with **Vulnerability as the headline at every level**, and two orthogonal moves:
**zoom** (get more local) and **lens** (repaint the same level). Need and supply are the
same map read two ways; the capstone is where they converge on a decision.

## 2. The three pieces, merged

### (A) Skeleton — one zoom spine, lens ⟂ zoom
- **Land on:** National, coloured by Vulnerability, supply dots off.
- **Drill:** region → IHA → small area, with a persistent breadcrumb (`Ireland › West › Donegal IHA › SA 067…`) and one "zoom out" control. This replaces the current split between `index.html` and `zoom.html`.
- **Lens** (a single control, never changes zoom): `Vulnerability` (default) · the 5 breakdowns (Care load / Strain / Demand / Isolation / **Service desert**) · `Market Gap` (IHA level only) · supply-dot overlays · legacy bivariates (collapsed "advanced").
- **IHA becomes a real middle rung**, not an orphan tab — that's where Market Gap lives.

### (B) Headline map — Need × Supply bivariate (the "opportunity" view)
- 3×3 Stevens bivariate of every small area: **Y = Vulnerability** (need) × **X = pr_distance** (rank of distance to nearest carer support). Dark corner = high need **and** far from help = **target here**.
- **Why bivariate, not just the multiply score:** it *disambiguates the muddy middle* — a "high-need-but-served" area and a "low-need-but-remote" area score the same on the multiply `service_desert`, but land in *different* cells here, so you see **which axis** drives each place.
- Both axes are 0–100 (percentile-rank / composite-of-ranks), tercile-split — statistically the standard, defensible bivariate (the same engine already in `index.html`).
- **The scalar `service_desert` score still powers the ranked "10 areas of greatest unmet need" table** — a scalar is the honest tool for an ordered list; the bivariate is the honest tool for the landscape. They cite each other.
- **Legacy bivariates demoted, as you asked:** re-key them onto the *same* need axis — `Vulnerability × no-car`, `Vulnerability × lone-homes` — so it's **one need axis, three swappable lenses** (distance = headline; no-car / lone = breakdowns inside the vulnerability story), not three competing front-page indices.

### (C) The answer — "Target", reached from two doors
The capstone is an **answer card** at the bottom of two drills that meet on the same geography:
- **Operator path:** IHA level → Market Gap lens → pick top-ranked IHA → card: *"Target your supply here"* (gap score, mean need, provider count, density) → **"see the deserts inside"** drills to that IHA's worst small areas. Plus a **downloadable target list (CSV)** — the commercial artifact.
- **Planner/family path:** drill to small areas → Service-desert lens + dots on → top-100 highlight + 10-area table → SA card: *"Greatest unmet need"* (vulnerability, km to nearest support + its precision flag, nearest FCI centre + phone).
- **One flip on the card — "market opportunity ⇄ unmet need" — toggles the two framings of the identical place.** That toggle *is* the product's thesis.

## 3. The colour trap, turned into the call-to-action
Region/IHA fills are **averages** (bunch ~40–60); small-area fills are **true values** (2–98). Fixes, as architectural rules:
1. **Each level gets its own colour breaks** (8 region means / 20 IHA means / 18,919 SA values) so no level looks washed out.
2. **Legend names what the colour is:** "Region average" vs "This area's own value".
3. **Spread bar** on every coarse-level tooltip: *"avg 48 · ranges 12→91 inside."*
4. **"Hidden hotspots" badge:** a muted region containing high-need pockets gets *"⚠ 31 top-decile small areas"* — which pulls users *into* the regions the average would have hidden.

## 4. What the METHODS chat builds (this chat)
Everything else is presentation (visuals chat). The new *data* work is small and bounded:

1. **`build_target_drilldown.py` → `data/target_drilldown.json`** — the capstone dataset.
   Join `sa_service_desert.csv` ⨝ `sa_to_iha.csv` on `sa_2022_code` (0 unassigned), group by
   `IHA_code`, take each IHA's top-M small areas by `service_desert`; attach the IHA's
   `iha_market_gap` row. Emit one JSON keyed by IHA: summary + list of top-M towns (with
   centroid lat/lon, desert score, nearest type/km, **`nearest_loc` precision flag**).
   ⚠ Join on the **code**, not the name; confirm both `IHA_code` read as the same type.
2. **Town names — the one genuinely new data task.** SA codes (`157110001`) are meaningless to
   a user. Reverse-geocode each target SA centroid **once, offline**, against a keyless Irish
   settlements layer (**CSO Settlements 2022** boundaries, or OSM `place=town/village` points),
   label as **"near Belmullet"** to signal it's the nearest settlement, not a postal address.
   Fallback to "Co. Mayo · SA 157110001" if nothing resolves within a sensible radius. Cache
   into the JSON — no live geocoding.
3. **Spread + hotspot precompute** — per region and per IHA, the internal 5th/95th vulnerability
   percentile and the count of top-decile SAs, baked into `regions.json` / an IHA meta file, so
   the spread bar and hotspot badge have data to show.

## 5. Honesty (carried from the data, must stay on-screen)
- **Office ≠ delivery location** — a home-care office may dispatch carers across counties; distance-to-nearest is a *proxy for access, not a service boundary*. The single biggest caveat — keep it on the decision surface, not a footer.
- **Geocoding precision varies** — home-care offices are mostly town-accurate (only 27/201 street-level); show the `nearest_loc` badge per town; a county-geocoded "nearest" is a softer claim. Most robust in rural deserts (offset small vs tens-of-km), which is where the signal matters.
- **Ranks are 0–100, not %.** Bivariate terciles are **relative to Ireland** (≈1/9 of areas always fall in the dark corner) — say so; it shows *where* the worst-on-both are, not an absolute count.
- **Frame the output as a shortlist to validate on the ground, never a verdict.** False precision driving a real-money "build here" decision is the capstone's biggest risk; the precision flags must travel with every number, including the CSV export.

## 6. Build order (lowest risk first)
1. **(C) operator answer** — pure join over existing scored CSVs; lowest risk, highest "actionability". Needs the town-name task.
2. **(B) bivariate headline** — near-zero new data (both axes already exist); reuses the proven bivariate engine.
3. **(A) unified flow** — the most engineering (merging two pages into one shell); the visuals chat's main job.

Stop at (C) and you already have the decisive "target your supply here" artifact. (B) and (A)
make it elegant and coherent.
