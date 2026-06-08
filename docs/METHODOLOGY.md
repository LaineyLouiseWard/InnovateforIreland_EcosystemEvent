# Methodology & grounding

The carer need-vs-supply map, end to end, and the established method each step rests on.
This is the single reference for *what we did and why it's defensible*. Data provenance is
in `SOURCES.md`; the product/UX concept is in `docs/CAPSTONE_CONCEPT.md`.

**Scope:** Republic of Ireland only (CSO Census 2022, Pobal, Tailte Éireann, HIQA, HSE).
**Geography:** 18,919 Census Small Areas (SA) sit inside 20 HSE Integrated Healthcare Areas
(IHA), which sit inside 8 NUTS3 regions. Everything is area-level; nothing identifies an
individual.

---

## 1. Demand: the Vulnerability Index (per Small Area)

A composite of four themes. Each input is percentile-ranked across all 18,919 SAs (0–100,
where 100 is the greatest need), the inputs are averaged within each theme, and the four
themes are averaged into one score.

| Theme | Input | Source |
|---|---|---|
| Care load | carer rate | CSO Census 2022 |
| Strain | Pobal HP Deprivation score (ED to SA via crosswalk) | Pobal 2022 |
| Demand | disability rate + % aged 65+ | CSO Census 2022 |
| Isolation | no-car households (plus distance-to-support, added in Plan 3) | CSO Census 2022 |

Grounded in the CDC/ATSDR Social Vulnerability Index (the percentile-rank-and-sum method)
and the OECD *Handbook on Constructing Composite Indicators*. Percentile ranking avoids
inventing weights and makes unlike variables (a %, a deprivation score, a rate) comparable.
We dropped the 43+hrs-caring variable because it does not exist at SA level in the census
(documented in `_archive/VARIABLE_VERIFICATION_REPORT.md`), rather than fabricate it.

## 2. Supply: three service-point layers

Geocoded point locations of where carer and older-person support physically exists: nursing
homes (HIQA register, 543), home-care agencies (20 HSE approved-provider lists, 206 distinct
offices), and Family Carers Ireland centres (16). Addresses were geocoded with OSM Nominatim
(keyless). Eircodes are not openly geocodable, so precision is street- or town-level, and the
precision flag travels with every point (see Limitations).

## 3. Service Desert: fusing demand and supply (per Small Area)

The link between *areas* (demand) and *points* (supply) is distance:
`Service Desert = Vulnerability × (percentile-rank of distance to nearest carer support)`.
It is multiplied, not averaged, so an area scores high only when it has both high need *and*
no support nearby. "Carer support" here means home care plus FCI. Nursing homes are excluded
from the distance, because a residential bed replaces home caring rather than supporting the
informal carer.

Grounded in the USDA Food Access Research Atlas, the reference standard for mapping
"deserts," which measures distance from each area to the *nearest* service, overlaid with
vehicle access (our no-car / Isolation theme) and low income (our deprivation / Strain
theme). We independently land on the same recipe, applied to carer support. We use the
nearest service rather than the average to all, because distant, irrelevant services would
pollute a mean.

### 3a. Supply density (context, not score)

Alongside nearest-distance we count carer-support services within 25 km of each area, a
realistic catchment (home-care carers travel roughly 20–30 minutes, FCI centres serve whole
counties). It catches the "one lonely office serving a huge area" case. This is a context
number only and does not feed the desert score. At 25 km, about 12% of areas have none
nearby.

## 4. Market Gap: operator view (per HSE area)

Roll SA vulnerability up to each of the 20 IHAs (population-weighted mean), count approved
providers per IHA (from the 20 HSE PDFs directly, not the deduped points), then:
`Market Gap = percentile-rank(need) − percentile-rank(provider density)`.

Grounded in standardised-score differencing, the recognised method for need-vs-provision
indices. We explicitly rejected a ratio (`need ÷ supply`): dividing percentile ranks
explodes when the denominator is the lowest-density area. It gave Kerry a "33", 9.7× the
next, a pure artifact. The difference is bounded [−100, +100], linear, comparable, and
re-ranks more sensibly (the highest-need area, Donegal, rises to its rightful place).

## 5. The Need × Supply bivariate (the "opportunity" view)

A 3×3 bivariate choropleth: need (Vulnerability) against supply access (distance rank),
terciles on each axis. The dark corner is high need plus far from help, the place to target.
It shows the *same* two ingredients as the desert score but un-fused, so you can see *which*
axis drives each area. That disambiguates "high-need-but-served" from "low-need-but-remote,"
which the single score blurs together.

Grounded in the Stevens bivariate choropleth, a standard cartographic technique;
need-vs-supply is one of its textbook applications.

## 6. Capstone: "target your supply here"

A pure join, no new modelling: the 20 IHAs ranked by Market Gap, each expanded to its worst
Service-Desert small areas. This is the literal "enter this HSE area, target these towns"
answer. Built by `scripts/build_target_drilldown.py`, written to `data/target_drilldown.json`.

---

## 7. Honesty & limitations (surfaced on-screen, not hidden)

*Full plain-language list in [`docs/LIMITATIONS.md`](LIMITATIONS.md). Summary:*

- **Office is not delivery location.** A home-care agency office is a registered business
  address; the carers it employs drive out to clients' homes across a wide area. So the office
  is where the provider is based, not where care is delivered. "Distance to nearest office" is
  a proxy for access, not a service boundary: an area 40 km from an office may still be served
  by a carer who drives there. This is the single biggest caveat.
- **Geocoding precision is uneven.** Home-care offices are the weak layer (only 27 of 201
  resolved to a street; most fell to the town centre, some to county). Every point carries a
  precision flag (`address`/`town`/`county`); county-level points are softer claims. The error
  matters least where the signal is strongest, in rural deserts, where true distances dwarf the
  offset. The upgrade path is a paid Eircode-to-coordinate lookup, which would sharpen every
  point: a bounded improvement, not a redesign.
- **Ranks are relative.** Percentile ranks and bivariate terciles are relative to Ireland
  ("worst third," not an absolute threshold). By construction about 1 in 9 areas falls in the
  bivariate's dark corner regardless of absolute conditions.
- **Ranks are 0–100 scores, not percentages.** Never relabel them "%".
- **Output is a shortlist to validate on the ground, never a verdict.** This matters most for
  the operator "build here" list, where false precision could drive a real-money decision.
- **ROI only.** Northern Ireland uses separate geography (NISRA) and a different deprivation
  index (NIMDM); an all-island version is a distinct piece of work.

## 8. What we deliberately rejected (the discipline)

- **Ratio Market Gap**, replaced with rank difference (artifact; see §4).
- **2SFCA** (two-step floating catchment, the health-access "gold standard"). It needs
  per-provider *capacity* data we don't have; using it would mean guessing the very numbers
  that make it better. Nearest-distance is the honest choice for our data.
- **Average distance to all services**, because distant services pollute it.
- **43+hrs caring variable**, which does not exist at SA level and was not fabricated.

## References

- CDC/ATSDR Social Vulnerability Index, methodology (percentile-rank-and-sum).
- OECD (2008), *Handbook on Constructing Composite Indicators*.
- USDA ERS, *Food Access Research Atlas* / *Mapping Food Deserts* (distance-to-nearest +
  vehicle access + income).
  https://www.ers.usda.gov/amber-waves/2011/december/data-feature-mapping-food-deserts-in-the-u-s
- Stevens, J., *Bivariate Choropleth Maps* (technique reference).
- Two-Step Floating Catchment Area method, https://en.wikipedia.org/wiki/Two-step_floating_catchment_area_method (considered, rejected for lack of capacity data).
- Standardised-score / rank-dependent composite indices: PMC4796338 (standardized scores pattern), PMC3158909 (rank-dependent indices, good practice).
- Pobal HP Deprivation Index 2022; CSO Census 2022 SAPS; HIQA Register of Designated Centres for Older People; HSE Approved Home-Support Provider lists. (Full URLs in `SOURCES.md`.)
