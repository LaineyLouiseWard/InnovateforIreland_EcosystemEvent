# Business research findings

Compiled 2026-06-08 from web research across three parallel agents.

---

## The confirmed market gap

Ireland has no equivalent of Carterwood Analytics (GB) or Oscar Research (UK) — the
dominant UK platforms for care sector site selection. Both are explicitly GB/UK only.
The closest Irish equivalent is poidata.io, which is a POI directory with no demand
modelling, no gap analysis, and no demographic overlays.

The academic literature confirms the same gap: a 2021 PMC composite-index study of
Irish nursing home access had to manually assemble datasets from HIQA, CSO, and HSE
because no integrated location intelligence exists.

**The product pitch is: Carterwood for Ireland.**

---

## Market size

| Sector | Revenue | Growth | Notes |
|---|---|---|---|
| Nursing homes | ~€800m | ~2% CAGR | 545 HIQA-registered homes; 10 investment funds now hold 1/3 of all beds |
| Home care | USD 2.9bn (2024) → USD 5.4bn (2030) | 11% CAGR | About to be regulated for first time (Health Amendment Bill, Dec 2025) |

Over-65 population set to double to 1.6m by 2051; over-80s (primary nursing home
users) up 271%. ESRI Hippocrates model projects 19,500–25,000 additional nursing home
beds needed by 2040. Only 443 delivered in 2024.

---

## Who pays

| Customer | Pain | Likelihood to pay |
|---|---|---|
| Nursing home developer/investor | Where do I build? Rural Fair Deal rates don't cover costs — need viable catchments | **High** — CBRE already charges for reactive valuation; a proactive tool fills a gap |
| Home care operator expanding | Which IHA should I apply for? Where is demand high, competition thin? | **High** — operational decision worth significant revenue |
| HSE / Family Carers Ireland planner | Where do we direct limited resources? | **Low** — free public tool or grant-funded; slow procurement |
| New care startup | Is my area viable before I commit? | **Medium** — lower spend capacity but high volume as sector opens up |

The primary paying customer is the **operator or investor**, not the planner.
The planner view (free, public-facing) is the credibility layer that makes the paid
product defensible.

---

## Supply side — what can actually be mapped

| Supply type | Geographic | Mappable now? | Source |
|---|---|---|---|
| Nursing homes | Physical locations | **Yes** | HIQA Jan 2026 register — 545 homes, public PDF download |
| Family Carers Ireland centres | 22 physical locations | **Yes** | fci.ie (already in _archive/CARER_SCOPING.md) |
| Home care agencies | IHA-level service areas | **Partially** — IHA boundaries yes, individual providers no | No register yet; Bill passed Dec 2025, 2-year window to register |
| Phone/national helplines | Not geographic | **No** — national coverage, no spatial gap | N/A |

Supply gap = nursing home beds per capita vs projected need (ESRI regional data).
Home care agency coverage gap will become mappable once HIQA registration opens (~2027).

---

## Two customer framings — same map, different front door

**Planner framing** ("where is suffering concentrated?")
- Demand: high carer rate + high deprivation + high disability
- Supply: nearby nursing home beds + FCI centres
- Output: where need is greatest and services are furthest away
- Customer: HSE, FCI, policy bodies

**Site-selection framing** ("where is my market?")
- Demand: same variables — population need
- Supply: existing competitor beds per capita
- Output: high need, low supply, viable Fair Deal catchment
- Customer: developers, operators, investors, new entrant startups

The data engine is identical. The UI framing and variable emphasis differ.

---

## Structural constraints on location decisions

- **Nursing homes**: HIQA registers per-site on quality, no geographic cap. Fair Deal
  rates set by NTPF, vary by county (Dublin €1,335/wk vs Donegal €1,125/wk — a
  €655k/yr gap per 60-bed home). Rural areas structurally unviable under current rates.
  Northwest (Donegal, Sligo, Leitrim, Roscommon) most underserved relative to need.

- **Home care**: HSE Authorisation Scheme assigns approved providers to specific IHAs
  (20 areas within 6 health regions). A new entrant must nominate which IHA(s) to serve
  and apply for authorisation. IHA boundaries are on GeoHive (free).

---

## Key sources

- [Carterwood Analytics (GB benchmark)](https://www.carterwood.co.uk/analytics-elderly-care-homes/)
- [HIQA nursing homes register, Jan 2026](https://www.hiqa.ie/sites/default/files/2026-01/List-of-centres-13-January-2026.pdf)
- [ESRI Hippocrates regional projections to 2040](https://www.esri.ie/publications/projections-of-regional-demand-and-bed-capacity-requirements-for-older-peoples-care-in)
- [BDO/NHI Private & Voluntary Nursing Home Survey 2023-24](https://www.bdo.ie/en-gb/news/2024/private-and-voluntary-nursing-home-survey-report-2023-24-by-bdo-ireland)
- [PMC composite access/need index for Irish nursing homes](https://pmc.ncbi.nlm.nih.gov/articles/PMC8669779)
- [HSE Home Support Authorisation Scheme SOP 2025](https://www.hse.ie/eng/services/list/4/olderpeople/home-support-authorisation-scheme-standard-operating-procedure-2025.pdf)
- [GeoHive: HSE Integrated Healthcare Areas 2025](https://www.geohive.ie/items/7c0665223cda494aa22b5dee643a0ac0)
- [HRB Open Research: composite indices for nursing home care in Ireland](https://hrbopenresearch.org/articles/3-65)
