# Brainstorm: problems to bring to the workshop

On the day each group proposes one or two real problems, then picks one to build. Jonathan's steer: bring the *problem*, lead with the frustration, and keep the data and feasibility in your back pocket for the "is it even possible?" question.

Two candidates below, both checked for free, keyless data. Both follow the same pattern as the example map: pull open data, join it to a boundary, score it, draw it with Leaflet.

## 1. UCD student housing finder (lead idea)

**How might we** help students moving to UCD, especially international students who don't know Dublin, find where they can afford to live within a reasonable commute, and tell whether a rent is fair, so newcomers stop overpaying, getting scammed, or landing a 90-minute commute?

**What it is:** a map that shows incoming students where they can afford to live and the commute time to campus, with a built-in rent-fairness check (enter area, unit, and your rent, and see whether it's over or under typical).

- Explore mode (map): typical rent by area, UCD pinned, commute-time shading.
- Check mode (input): a unit toggle solves the per-room problem. A whole dwelling benchmarks against RTB; a room shared with others benchmarks against Daft room rents.

**Data (verified):**
- RTB / ESRI Rent Index: standardised rents at Local Electoral Area (166 LEAs), split by house/apartment and bedrooms, quarterly. Cells with fewer than 30 observations are suppressed, so use a fallback ladder (LEA + type + beds, then LEA all-apartments, then county).
- Daft Room Rental Report: per-room rents (the student unit). Dublin-dense, which suits UCD, but these are asking prices at coarser geography.
- Commute: GTFS (Transport for Ireland) for real transit time is the hard part. Version one uses road or straight-line distance to UCD, clearly labelled "approx"; the transit version is the "we'd extend it to..." line.
- Geocoding: Eircode to LEA by point-in-polygon (GeoHive boundaries).
- The "rent you were quoted" side is user input, not a dataset.

**Scope and positioning:** keep it to UCD for the workshop (dense data, easy to demo, and lived credibility). It generalises to other colleges, though room data thins outside Dublin. UK tools prove the concept (Rightmove's "Where Can I Live", CloseMove); there's no equivalent for the Republic, so it's a real gap.

## 2. Carer vulnerability map (health-flavoured)

**How might we** help carer support services and the HSE see where the most vulnerable unpaid carers are concentrated, the ones who are also poor, elderly, or isolated, so support reaches the carers most at risk of burnout before they hit crisis?

**The design crux: no arbitrary composite index.** A weighted carers × hours × health score needs weights you can't defend (the same trap the fun index plays with on purpose). Instead use quartile overlap: rank small areas on two real measures and flag the areas in the worst quartile on both. It's defensible because you never invent a weight, you just say "worst 25% on both." Show it as a bivariate choropleth, or highlight the overlap.

**Three overlays, each a distinct frustration:**
1. Carer rate × deprivation: carers under financial strain who can't afford private respite.
2. Older carers (65+): people caring at an age when they may need care themselves.
3. Carer rate × isolation: distance to the nearest Family Carers Ireland centre (there are only 22) and/or low car availability.

**Data (all real, checked):**
- Carer rate: Census 2022 SAPS at Small Area level (Q23, plus hours-per-week bands to isolate the 43+ hour carers). Roughly 300k carers nationally; Mayo highest at about 7%, Dublin City about 5%.
- Deprivation: Pobal HP Deprivation Index, a ready-made standardised score per small area.
- Car availability: census SAPS.
- Family Carers Ireland: 22 support centres.

**Caveats:** the plain "where are the carers" map already exists (CSO SAPmap, AIRO Maynooth), so the novelty is the vulnerability overlays, not the base map; pitch it that way. Person-level cross-tabs (carers who are themselves poor or unwell) need microdata, so stick to area-rate overlays. Don't lean on the 2016-to-2022 "up 53%" growth figure, since the question wording changed; lead with scale and distribution instead.
